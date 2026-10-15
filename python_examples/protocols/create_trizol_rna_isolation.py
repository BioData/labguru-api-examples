"""
Create a Labguru protocol for TRIzol Reagent total RNA isolation.

Source: Invitrogen TRIzol Reagent User Guide, Pub. No. MAN0001271 Rev. D
https://assets.thermofisher.com/TFS-Assets/LSG/manuals/trizol_reagent.pdf

Related guides (referenced in the protocol description):
- TRIzol Reagent and Phasemaker Tubes Complete System, Pub. No. MAN0016163
- TRIzol Reagent (DNA isolation), Pub. No. MAN0016385

The protocol content lives in trizol_protocol_content.py; this file is only the API flow.
Protocol content is reproduced from Thermo Fisher Scientific documentation (MAN0001271),
(c) Thermo Fisher Scientific Inc., for demonstration of the Labguru API only.
Trademarks are the property of Thermo Fisher Scientific and its subsidiaries.

The PDF user guides are not stored in this repo; the script downloads them from Thermo Fisher at run time.

What the script does:
 1. POST /api/v1/protocols            - create the protocol ("item" is a JSON-encoded string)
 2. GET  /api/v1/protocols/{id}       - find the default "Description" and "Procedure" sections
 3. PUT  /api/v1/elements/{id}        - fill the default Description text element
 4. POST /api/v1/sections             - add a section per stage (PUT renames the default Procedure section)
 5. DELETE /api/v1/elements/{id}      - remove the empty text element Labguru adds to each new section
 6. POST /api/v1/elements             - add "steps" and "text" elements
 7. GET/POST /api/v1/materials        - find or create the reagents (consumables)
    GET/POST /api/v1/instruments      - find or create the equipment
 8. POST /api/v1/samples              - link each reagent / instrument to a "samples" / "equipment" element,
    PUT  /api/v1/elements/{id}          then write the element data so the items show in the table
 9. POST /api/v1/attachments          - upload the Thermo Fisher PDF manuals to the protocol,
    PUT  /api/v1/attachments/{id}       then link them to an "attachments" element

Usage:
    export LABGURU_TOKEN=...            (or put the token in token.dat at the repo root)
    python create_trizol_rna_isolation.py [https://my.labguru.com]

Re-running the script creates a new protocol, but reuses reagents and equipment with the same name.
If a run fails partway, the script deletes the half-built protocol (or prints its URL if it can't).
"""

import json
import os
import sys

import requests

from trizol_protocol_content import (
    DESCRIPTION_HTML,
    EQUIPMENT,
    MANUALS,
    PROCEDURE_SECTIONS,
    PROTOCOL_NAME,
    REAGENTS,
)

SERVER_BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://my.labguru.com").rstrip("/")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "token.dat")

HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30  # seconds, for API calls
UPLOAD_TIMEOUT = 120  # seconds, for PDF downloads and uploads


def load_token():
    token = os.environ.get("LABGURU_TOKEN")
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
    if not token:
        token = input("Enter token: ").strip()
    return token


def text(name, html):
    return {"element_type": "text", "name": name, "data": html}


def steps(name, step_list):
    # The steps element stores its data as a JSON string of step objects
    return {"element_type": "steps", "name": name, "data": json.dumps(step_list)}


# ---------------------------------------------------------------------------
# Labguru API calls
# ---------------------------------------------------------------------------


class ApiError(Exception):
    pass


def api(method, path, token, payload=None):
    url = f"{SERVER_BASE}/api/v1/{path}"
    if method in ("GET", "DELETE"):
        response = requests.request(method, url, params={"token": token}, timeout=TIMEOUT)
    else:
        body = dict(payload or {}, token=token)
        response = requests.request(method, url, headers=HEADERS, data=json.dumps(body), timeout=TIMEOUT)
    if response.status_code not in (200, 201, 204):
        raise ApiError(f"{method} {path} failed. Status: {response.status_code}. Response: {response.text[:1000]}")
    try:
        return response.json()
    except ValueError:
        return {}


def create_protocol(token):
    # The protocols endpoint expects "item" as a JSON-encoded string, not an object
    item = json.dumps({"name": PROTOCOL_NAME, "experiment_procedures": [], "elements": []})
    protocol = api("POST", "protocols", token, {"item": item})
    print(f"Protocol created. ID: {protocol['id']}")
    return protocol["id"]


def get_default_sections(token, protocol_id):
    """Returns {section_type: section} for the sections Labguru creates with a new protocol."""
    protocol = api("GET", f"protocols/{protocol_id}", token)
    sections = [s["experiment_procedure"] for s in protocol.get("experiment_procedures", [])]
    return {s["section_type"]: s for s in sections}


def add_section(token, protocol_id, name, position):
    section = api(
        "POST",
        "sections",
        token,
        {
            "item": {
                "name": name,
                "container_id": protocol_id,
                "container_type": "Knowledgebase::Protocol",
                "position": position,
            }
        },
    )
    print(f"Section '{name}' created. ID: {section['id']}")
    return section["id"]


def rename_section(token, protocol_id, section_id, name):
    # Sections follow the usual Rails shape: the fields go under "item"
    api(
        "PUT",
        f"sections/{section_id}",
        token,
        {"item": {"name": name, "container_id": protocol_id, "container_type": "Knowledgebase::Protocol"}},
    )
    print(f"Section {section_id} renamed to '{name}'.")


def add_element(token, section_id, element):
    item = dict(element, container_id=section_id, container_type="ExperimentProcedure")
    created = api("POST", "elements", token, {"item": item})
    print(f"  {element['element_type']} element '{element['name']}' added. ID: {created['id']}")
    return created["id"]


def update_text_element(token, element_id, html):
    # PUT /elements takes "data" at the top level, NOT under "item" (wrapping it in "item" returns 422).
    # For a text element, data is the HTML itself.
    api("PUT", f"elements/{element_id}", token, {"data": html})
    print(f"  Text element {element_id} updated.")


def remove_empty_text_elements(token, section_id):
    """New sections come with an empty text element. Call this before adding content."""
    section = api("GET", f"sections/{section_id}", token)
    for element in section.get("elements", []):
        if element["element_type"] != "text":
            continue
        if api("GET", f"elements/{element['id']}", token).get("data"):
            continue
        api("DELETE", f"elements/{element['id']}", token)
        print(f"  Empty placeholder element {element['id']} removed.")


def find_or_create(token, endpoint, item):
    """Return an existing inventory item with the same name, or create it.

    The name is matched on the server (exact match) so the whole inventory is not paged through.
    """
    url = f"{SERVER_BASE}/api/v1/{endpoint}"
    params = {
        "token": token,
        "kendo": "true",
        "filter[logic]": "and",
        "filter[filters][0][field]": "name",
        "filter[filters][0][operator]": "eq",
        "filter[filters][0][value]": item["name"],
    }
    response = requests.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    results = response.json()
    if not isinstance(results, list):
        raise ApiError(f"GET {endpoint} returned an unexpected response: {str(results)[:200]}")
    # Check the name too: if the server ignored the filter, it would return unrelated items
    matches = [m for m in results if m.get("name") == item["name"]]
    if matches:
        existing = matches[0]
        print(f"  Using existing {endpoint} {existing['id']}: {item['name']}")
        return existing
    created = api("POST", endpoint, token, {"item": item})
    print(f"  Created {endpoint} {created['id']}: {item['name']}")
    return created


def link_items(token, element_id, item_class, collection_name, items):
    """Link inventory items to a samples/equipment element.

    POST /samples creates the link; the element's data must then list the samples
    so they are shown in the element's table.
    """
    element = api("GET", f"elements/{element_id}", token)
    data = element["data"] if isinstance(element["data"], dict) else json.loads(element["data"] or "{}")
    data.setdefault("headers", {})
    data["samples"] = []
    for item in items:
        sample = api(
            "POST",
            "samples",
            token,
            {"item": {"container_type": "Element", "container_id": element_id,
                      "item_id": item["id"], "item_type": item_class}},
        )
        data["samples"].append({
            "id": sample["id"],
            "name": item["name"],
            "url": item.get("url"),
            "collection_name": collection_name,
            "data": item,
            "item": {"item_class": item_class, "item_id": item["id"], "generic_collection_id": None},
            "container": {"type": "Element", "id": element_id},
            "remarks": None,
            "properties": [],
            "stocks": [],
            "selected_stocks": [],
            "saved_stocks_ids": [],
            "select_all_stocks": False,
            "storages": [],
        })
    # Same top-level "data" as update_text_element, but samples/equipment elements store a JSON object,
    # so it is sent as a JSON-encoded string
    api("PUT", f"elements/{element_id}", token, {"data": json.dumps(data)})
    print(f"  Linked {len(items)} {collection_name.lower()} to element {element_id}.")


def upload_manual(token, protocol_uuid, filename, url, description):
    pdf = requests.get(url, timeout=UPLOAD_TIMEOUT)
    pdf.raise_for_status()
    response = requests.post(
        f"{SERVER_BASE}/api/v1/attachments",
        data={
            "token": token,
            "item[title]": filename,
            "item[description]": description,
            "item[attach_to_uuid]": protocol_uuid,
        },
        files={"item[attachment]": (filename, pdf.content, "application/pdf")},
        timeout=UPLOAD_TIMEOUT,
    )
    if response.status_code != 201:
        raise ApiError(f"Upload of {filename} failed. Status: {response.status_code}. Response: {response.text[:1000]}")
    attachment = response.json()
    print(f"  Uploaded {filename}. Attachment ID: {attachment['id']}")
    return attachment["id"]


def build_protocol(token, protocol_id):
    defaults = get_default_sections(token, protocol_id)

    # Description section: fill its empty text element (or add one)
    description = defaults.get("description")
    if description:
        text_elements = [e for e in description["elements"] if e["element_type"] == "text"]
        if text_elements:
            update_text_element(token, text_elements[0]["id"], DESCRIPTION_HTML)
        else:
            add_element(token, description["id"], text("Description", DESCRIPTION_HTML))
    else:
        section_id = add_section(token, protocol_id, "Description", 1)
        add_element(token, section_id, text("Description", DESCRIPTION_HTML))

    # Materials: reuse the default "Procedure" section, link reagents and equipment from inventory
    procedure = defaults.get("procedure")
    if procedure:
        section_id = procedure["id"]
        rename_section(token, protocol_id, section_id, "Materials and equipment")
    else:
        section_id = add_section(token, protocol_id, "Materials and equipment", 2)
    remove_empty_text_elements(token, section_id)

    reagents = [find_or_create(token, "materials", item) for item in REAGENTS]
    element_id = add_element(token, section_id, {"element_type": "samples", "name": "Reagents", "data": ""})
    link_items(token, element_id, "Catalog::Material", "Consumables", reagents)

    instruments = [find_or_create(token, "instruments", item) for item in EQUIPMENT]
    element_id = add_element(token, section_id, {"element_type": "equipment", "name": "Equipment", "data": ""})
    link_items(token, element_id, "System::Instrument", "Instruments", instruments)

    # Procedure stages
    for index, (name, element_type, content) in enumerate(PROCEDURE_SECTIONS):
        section_id = add_section(token, protocol_id, name, index + 3)
        remove_empty_text_elements(token, section_id)
        element = steps(name, content) if element_type == "steps" else text(name, content)
        add_element(token, section_id, element)

    # Reference manuals: upload the PDFs to the protocol, then show them in an attachments element
    section_id = add_section(token, protocol_id, "Reference manuals", len(PROCEDURE_SECTIONS) + 3)
    remove_empty_text_elements(token, section_id)
    element_id = add_element(token, section_id, {"element_type": "attachments", "name": "Thermo Fisher user guides", "data": ""})
    protocol_uuid = api("GET", f"protocols/{protocol_id}", token)["uuid"]
    for filename, url, description in MANUALS:
        attachment_id = upload_manual(token, protocol_uuid, filename, url, description)
        # Attachments use the Rails "item" shape; element_id moves the file into the attachments element
        api("PUT", f"attachments/{attachment_id}", token, {"item": {"element_id": element_id}})


def main():
    token = load_token()
    protocol_id = create_protocol(token)
    protocol_url = f"{SERVER_BASE}/knowledge/protocols/{protocol_id}"
    try:
        build_protocol(token, protocol_id)
    except (ApiError, requests.RequestException) as error:
        # Don't leave a half-built protocol behind. Inventory items created so far are kept;
        # the next run reuses them by name.
        print(f"\nFailed: {error}")
        try:
            api("DELETE", f"protocols/{protocol_id}", token)
            print(f"Deleted the half-built protocol {protocol_id}.")
        except (ApiError, requests.RequestException):
            print(f"Could not delete the half-built protocol. Delete it by hand: {protocol_url}")
        sys.exit(1)
    print(f"\nDone: {protocol_url}")


if __name__ == "__main__":
    main()
