"""
Create a Labguru protocol for TRIzol Reagent total RNA isolation.

Source: Invitrogen TRIzol Reagent User Guide, Pub. No. MAN0001271 Rev. D
https://assets.thermofisher.com/TFS-Assets/LSG/manuals/trizol_reagent.pdf

Related guides (referenced in the protocol description):
- TRIzol Reagent and Phasemaker Tubes Complete System, Pub. No. MAN0016163
- TRIzol Reagent (DNA isolation), Pub. No. MAN0016385

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
"""

import json
import os
import sys

import requests

SERVER_BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://my.labguru.com").rstrip("/")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "token.dat")

PROTOCOL_NAME = "TRIzol Reagent total RNA isolation"

HEADERS = {"Content-Type": "application/json"}


def load_token():
    token = os.environ.get("LABGURU_TOKEN")
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
    if not token:
        token = input("Enter token: ").strip()
    return token


def step(title, hours=0, minutes=0, seconds=0):
    """A single step in a Labguru "steps" element. title is HTML."""
    return {
        "title": title if title.startswith("<") else f"<p>{title}</p>",
        "timer": {
            "hours": f"{hours:02d}",
            "minutes": f"{minutes:02d}",
            "seconds": f"{seconds:02d}",
        },
        "completed": False,
    }


def text(name, html):
    return {"element_type": "text", "name": name, "data": html}


def steps(name, step_list):
    # The steps element stores its data as a JSON string of step objects
    return {"element_type": "steps", "name": name, "data": json.dumps(step_list)}


# ---------------------------------------------------------------------------
# Protocol content (TRIzol Reagent User Guide, MAN0001271 Rev. D)
# ---------------------------------------------------------------------------

# Banner shown at the top of the protocol, so nobody mistakes the example for a validated lab protocol
DEMO_BANNER_HTML = """
<p style="background-color: #fff3cd; border: 2px solid #d9534f; color: #a94442; padding: 10px; text-align: center; font-size: 16px;">
<b>FOR DEMO PURPOSES ONLY</b><br>
This protocol was created by a Labguru API example. Follow the official Thermo Fisher user guide for lab work.</p>
"""

DESCRIPTION_HTML = DEMO_BANNER_HTML + """
<p><b>WARNING!</b> Read the Safety Data Sheets (SDSs) and follow the handling instructions.
Wear appropriate protective eyewear, clothing, and gloves.</p>

<p>Invitrogen&trade; TRIzol&trade; Reagent is a ready-to-use monophasic solution of phenol,
guanidine isothiocyanate, and other components for isolating high quality total RNA (as well as
DNA and proteins) from cell and tissue samples of human, animal, plant, yeast, or bacterial origin,
within one hour. After homogenizing the sample with TRIzol&trade; Reagent, chloroform is added and
the homogenate separates into a clear upper aqueous layer (containing RNA), an interphase, and a red
lower organic layer (containing the DNA and proteins). RNA is precipitated from the aqueous layer
with isopropanol, washed, and resuspended for downstream applications (RT-PCR, Northern blot,
dot blot, poly(A)+ selection, in vitro translation, RNase protection assay, molecular cloning).</p>

<p><b>Source:</b> TRIzol&trade; Reagent User Guide, Pub. No. MAN0001271 Rev. D (Cat. Nos. 15596026, 15596018).
Store TRIzol&trade; Reagent at 2&ndash;25&deg;C.</p>

<h3>Materials required (not supplied)</h3>
<table border="1" cellpadding="4">
  <tr><th>Item</th><th>Used for</th></tr>
  <tr><td>Centrifuge and rotor capable of reaching 12,000 &times; g and 4&deg;C</td><td>All isolations</td></tr>
  <tr><td>Polypropylene microcentrifuge tubes</td><td>All isolations</td></tr>
  <tr><td>Chloroform</td><td>All isolations</td></tr>
  <tr><td>Water bath or heat block at 55&ndash;60&deg;C</td><td>RNA isolation</td></tr>
  <tr><td>Isopropanol</td><td>RNA isolation</td></tr>
  <tr><td>Ethanol, 75%</td><td>RNA isolation</td></tr>
  <tr><td>RNase-free water or 0.5% SDS</td><td>RNA isolation</td></tr>
  <tr><td>(Optional) RNase-free glycogen or 0.1 mM EDTA</td><td>RNA isolation</td></tr>
</table>

<h3>Input sample requirements</h3>
<p><b>IMPORTANT!</b> Perform RNA isolation immediately after sample collection or quick-freeze
samples immediately after collection and store at &ndash;80&deg;C or in liquid nitrogen until RNA isolation.</p>
<table border="1" cellpadding="4">
  <tr><th>Sample type</th><th>Starting material per 1 mL of TRIzol&trade; Reagent</th></tr>
  <tr><td>Tissues (fresh, or stored in RNAlater&trade; Stabilization Solution)</td><td>50&ndash;100 mg of tissue</td></tr>
  <tr><td>Cells grown in monolayer</td><td>1 &times; 10<sup>5</sup>&ndash;1 &times; 10<sup>7</sup> cells grown in monolayer in a 3.5-cm culture dish (10 cm<sup>2</sup>)</td></tr>
  <tr><td>Cells grown in suspension</td><td>5&ndash;10 &times; 10<sup>6</sup> cells from animal, plant, or yeast origin or 1 &times; 10<sup>7</sup> cells of bacterial origin</td></tr>
</table>

<h3>Procedural guidelines</h3>
<ul>
  <li>Perform all steps at room temperature (20&ndash;25&deg;C) unless otherwise noted.</li>
  <li>Use cold TRIzol&trade; Reagent if the starting material contains high levels of RNase, such as spleen or pancreas samples.</li>
  <li>Use disposable, individually wrapped, sterile plasticware and sterile, disposable RNase-free pipettes, pipette tips, and tubes.</li>
  <li>Wear disposable gloves while handling reagents and RNA samples; change gloves frequently.</li>
  <li>Always use proper microbiological aseptic techniques when working with RNA.</li>
  <li>Use RNaseZap&trade; RNase Decontamination Solution (Cat. No. AM9780) to remove RNase contamination from work surfaces and non-disposable items.</li>
  <li>Ensure that all materials that come into contact with TRIzol&trade; Reagent are compatible with phenol, guanidine isothiocyanate, and chloroform.</li>
</ul>

<h3>Related protocols</h3>
<ul>
  <li><b>Phasemaker&trade; Tubes variant</b> (Cat. No. A33248): the Phasemaker&trade; gel forms a solid barrier between
  the organic and aqueous phases, which makes phase separation easier. See TRIzol&trade; Reagent and Phasemaker&trade;
  Tubes Complete System User Guide, Pub. No. MAN0016163.</li>
  <li><b>DNA isolation</b> from the saved interphase/organic phase: see TRIzol&trade; Reagent (DNA isolation) User Guide,
  Pub. No. MAN0016385.</li>
</ul>
"""

LYSE_STEPS = [
    step(
        "<p>Lyse and homogenize samples in TRIzol&trade; Reagent according to your starting material:</p>"
        "<ul>"
        "<li><b>Tissues:</b> Add 1 mL of TRIzol&trade; Reagent per 50&ndash;100 mg of tissue to the sample and homogenize using a homogenizer.</li>"
        "<li><b>Cells grown in monolayer:</b> Remove growth media. Add 1 mL of TRIzol&trade; Reagent per 1 &times; 10<sup>5</sup>&ndash;1 &times; 10<sup>7</sup> "
        "cells directly to the 3.5-cm culture dish to lyse the cells. Pipet the lysate up and down several times to homogenize.</li>"
        "<li><b>Cells grown in suspension:</b> Collect the cells by centrifugation and discard the supernatant. Add 1 mL of TRIzol&trade; Reagent "
        "per 0.25 mL of sample (5&ndash;10 &times; 10<sup>6</sup> cells from animal, plant, or yeast origin or 1 &times; 10<sup>7</sup> cells of bacterial origin) "
        "to the pellet. Pipet the lysate up and down several times to homogenize. "
        "<i>Note: Do not wash cells before addition of TRIzol&trade; Reagent to avoid mRNA degradation.</i></li>"
        "</ul>"
        "<p><i>Note: The sample volume should not exceed 25% of the volume of TRIzol&trade; Reagent used for lysis.</i></p>"
        "<p><b>STOPPING POINT</b> Samples can be stored at 4&deg;C overnight or at &ndash;20&deg;C for up to a year.</p>"
    ),
    step(
        "(Optional) If samples have a high fat content, centrifuge the lysate for 5 minutes at 12,000 &times; g "
        "at 4&ndash;10&deg;C, then transfer the clear supernatant to a new tube.",
        minutes=5,
    ),
    step("Incubate for 5 minutes to allow complete dissociation of the nucleoproteins complex.", minutes=5),
    step(
        "Add 0.2 mL of chloroform per 1 mL of TRIzol&trade; Reagent used for lysis, securely cap the tube, "
        "then thoroughly mix by shaking."
    ),
    step("Incubate for 2&ndash;3 minutes.", minutes=3),
    step(
        "<p>Centrifuge the sample for 15 minutes at 12,000 &times; g at 4&deg;C.</p>"
        "<p>The mixture separates into a lower phenol-chloroform, an interphase, and a colorless upper aqueous phase.</p>",
        minutes=15,
    ),
    step(
        "<p>Transfer the aqueous phase containing the RNA to a new tube by angling the tube at 45&deg; and pipetting the solution out.</p>"
        "<p><b>IMPORTANT!</b> Avoid transferring any of the interphase or organic layer into the pipette when removing the aqueous phase.</p>"
        "<p>To isolate DNA or protein, save the interphase and organic phase (see TRIzol&trade; Reagent (DNA isolation) "
        "User Guide, MAN0016385). The organic phase can be stored at 4&deg;C overnight.</p>"
    ),
]

PRECIPITATE_STEPS = [
    step(
        "<p>(Optional) If the starting sample is small (&lt;10<sup>6</sup> cells or &lt;10 mg of tissue), add 5&ndash;10 &micro;g "
        "of RNase-free glycogen as a carrier to the aqueous phase.</p>"
        "<p><i>Note: The glycogen is co-precipitated with the RNA, but does not interfere with subsequent applications.</i></p>"
    ),
    step("Add 0.5 mL of isopropanol to the aqueous phase, per 1 mL of TRIzol&trade; Reagent used for lysis."),
    step("Incubate for 10 minutes at room temperature (15&ndash;30&deg;C).", minutes=10),
    step(
        "<p>Centrifuge for 10 minutes at 12,000 &times; g at 4&deg;C.</p>"
        "<p>Total RNA precipitate forms a white gel-like pellet at the bottom of the tube.</p>",
        minutes=10,
    ),
    step("Discard the supernatant with a micropipettor."),
]

WASH_STEPS = [
    step(
        "<p>Resuspend the pellet in 1 mL of 75% ethanol per 1 mL of TRIzol&trade; Reagent used for lysis.</p>"
        "<p><i>Note: The RNA can be stored in 75% ethanol for at least 1 year at &ndash;20&deg;C, or at least 1 week at 4&deg;C.</i></p>"
    ),
    step("Vortex the sample briefly, then centrifuge for 5 minutes at 7500 &times; g at 4&deg;C.", minutes=5),
    step("Discard the supernatant with a micropipettor."),
    step(
        "<p>Vacuum or air dry the RNA pellet for 5&ndash;10 minutes.</p>"
        "<p><b>IMPORTANT!</b> Do not dry the pellet by vacuum centrifuge. Do not let the RNA pellet dry, to ensure total "
        "solubilization of the RNA. Partially dissolved RNA samples have an A230/280 ratio &lt;1.6.</p>",
        minutes=10,
    ),
]

SOLUBILIZE_STEPS = [
    step(
        "<p>Resuspend the pellet in 20&ndash;50 &micro;L of RNase-free water, 0.1 mM EDTA, or 0.5% SDS solution by pipetting up and down.</p>"
        "<p><b>IMPORTANT!</b> Do not dissolve the RNA in 0.5% SDS if the RNA is to be used in subsequent enzymatic reactions.</p>"
    ),
    step("Incubate in a water bath or heat block set at 55&ndash;60&deg;C for 10&ndash;15 minutes.", minutes=15),
    step("Proceed to downstream applications, or store the RNA at &ndash;70&deg;C."),
]

YIELD_HTML = """
<p>Determine the RNA yield using one of the following methods.</p>
<table border="1" cellpadding="4">
  <tr><th>Method</th><th>Procedure</th></tr>
  <tr>
    <td><b>Absorbance</b><br>A260 provides total nucleic acid content, while A280 determines sample purity.
    Free nucleotides, RNA, ssDNA, and dsDNA all absorb at 260 nm.</td>
    <td>
      <ol type="a">
        <li>Dilute sample in RNase-free water, then measure absorbance at 260 nm and 280 nm.</li>
        <li>Calculate the RNA concentration: A260 &times; dilution &times; 40 = &micro;g RNA/mL.</li>
        <li>Calculate the A260/A280 ratio. A ratio of ~2 is considered pure.</li>
      </ol>
      RNA samples can be quantified without prior dilution using the NanoDrop&trade; Spectrophotometer.
    </td>
  </tr>
  <tr>
    <td><b>Fluorescence</b><br>Selectively measures intact RNA, not protein or other contaminants.</td>
    <td>Quantify RNA yield using the appropriate Qubit&trade; or Quant-iT&trade; RNA Assay Kit
    (Cat. Nos. Q32852, Q10210, Q33140, or Q10213).</td>
  </tr>
</table>

<h4>Typical RNA (A260/280 of &gt;1.8) yields from various starting materials</h4>
<table border="1" cellpadding="4">
  <tr><th>Starting material</th><th>Quantity</th><th>RNA yield</th></tr>
  <tr><td>Epithelial cells</td><td>1 &times; 10<sup>6</sup> cells</td><td>8&ndash;15 &micro;g</td></tr>
  <tr><td>New tobacco leaf</td><td>&mdash;</td><td>73 &micro;g</td></tr>
  <tr><td>Fibroblasts</td><td>1 &times; 10<sup>6</sup> cells</td><td>5&ndash;7 &micro;g</td></tr>
  <tr><td>Skeletal muscles and brain</td><td>1 mg</td><td>1&ndash;1.5 &micro;g</td></tr>
  <tr><td>Placenta</td><td>1 mg</td><td>1&ndash;4 &micro;g</td></tr>
  <tr><td>Liver</td><td>1 mg</td><td>6&ndash;10 &micro;g</td></tr>
  <tr><td>Kidney</td><td>1 mg</td><td>3&ndash;4 &micro;g</td></tr>
</table>
"""

# Reagents (Labguru "consumables", class Catalog::Material). Commercial items need a catalog number.
REAGENTS = [
    {"name": "TRIzol Reagent", "produce_by": "Thermo Fisher", "catalog_number": "15596026",
     "description": "Store at 2-25°C. User guide: Pub. No. MAN0001271."},
    {"name": "Chloroform", "produce_by": "MLS", "description": "Required for TRIzol phase separation"},
    {"name": "Isopropanol", "produce_by": "MLS", "description": "RNA precipitation"},
    {"name": "Ethanol, 75%", "produce_by": "MLS", "description": "RNA wash"},
    {"name": "RNase-free water", "produce_by": "MLS", "description": "RNA solubilization (or 0.1 mM EDTA / 0.5% SDS)"},
    {"name": "RNase-free glycogen", "produce_by": "MLS", "description": "Optional carrier for small samples"},
    {"name": "RNaseZap RNase Decontamination Solution", "produce_by": "Thermo Fisher", "catalog_number": "AM9780",
     "description": "Removes RNase contamination from work surfaces and equipment"},
]

# Equipment (Labguru "instruments", class System::Instrument)
EQUIPMENT = [
    {"name": "Refrigerated microcentrifuge (12,000 x g, 4°C)", "equipment_type": "Centrifuge",
     "description": "Centrifuge and rotor capable of reaching 12,000 x g and 4°C"},
    {"name": "Water bath / heat block (55-60°C)", "equipment_type": "Heat block",
     "description": "Used to solubilize the RNA pellet"},
    {"name": "Tissue homogenizer", "equipment_type": "Homogenizer",
     "description": "Used to homogenize tissue samples in TRIzol Reagent"},
]

# Manuals attached to the protocol
MANUALS = [
    ("TRIzol_Reagent_User_Guide_MAN0001271.pdf",
     "https://assets.thermofisher.com/TFS-Assets/LSG/manuals/trizol_reagent.pdf",
     "TRIzol Reagent User Guide (Pub. No. MAN0001271) - source of this protocol"),
    ("TRIzol_Phasemaker_Tubes_UG_MAN0016163.pdf",
     "https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0016163_TRIzol_Phasemaker_Tubes_UG.pdf",
     "TRIzol Reagent and Phasemaker Tubes Complete System User Guide (Pub. No. MAN0016163)"),
    ("TRIzol_Reagent_DNA_Isolation_UG_MAN0016385.pdf",
     "https://assets.thermofisher.com/TFS-Assets/LSG/manuals/MAN0016385_TRIzol_Reagent_DNA_Isol_UG.pdf",
     "TRIzol Reagent (DNA isolation) User Guide (Pub. No. MAN0016385)"),
]

# Procedure stages, each created as a new section in this order
PROCEDURE_SECTIONS = [
    {"name": "Lyse samples and separate phases", "elements": [steps("Lyse samples and separate phases", LYSE_STEPS)]},
    {"name": "Precipitate the RNA", "elements": [steps("Precipitate the RNA", PRECIPITATE_STEPS)]},
    {"name": "Wash the RNA", "elements": [steps("Wash the RNA", WASH_STEPS)]},
    {"name": "Solubilize the RNA", "elements": [steps("Solubilize the RNA", SOLUBILIZE_STEPS)]},
    {"name": "Determine the RNA yield", "elements": [text("RNA yield", YIELD_HTML)]},
]


# ---------------------------------------------------------------------------
# Labguru API calls
# ---------------------------------------------------------------------------


def api(method, path, token, payload=None):
    url = f"{SERVER_BASE}/api/v1/{path}"
    if method in ("GET", "DELETE"):
        response = requests.request(method, url, params={"token": token})
    else:
        body = dict(payload or {}, token=token)
        response = requests.request(method, url, headers=HEADERS, data=json.dumps(body))
    if response.status_code not in (200, 201, 204):
        print(f"{method} {path} failed. Status: {response.status_code}")
        print("Response:", response.text[:1000])
        sys.exit(1)
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
    """Return an existing inventory item with the same name, or create it."""
    page = 1
    while True:
        items = api("GET", f"{endpoint}?page={page}", token)
        if not items:
            break
        for existing in items:
            if existing.get("name", "").strip() == item["name"]:
                print(f"  Using existing {endpoint} {existing['id']}: {item['name']}")
                return existing
        page += 1
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
    api("PUT", f"elements/{element_id}", token, {"data": json.dumps(data)})
    print(f"  Linked {len(items)} {collection_name.lower()} to element {element_id}.")


def upload_manual(token, protocol_uuid, filename, url, description):
    pdf = requests.get(url, timeout=60)
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
    )
    if response.status_code != 201:
        print(f"Upload of {filename} failed. Status: {response.status_code}")
        print("Response:", response.text[:1000])
        sys.exit(1)
    attachment = response.json()
    print(f"  Uploaded {filename}. Attachment ID: {attachment['id']}")
    return attachment["id"]


def main():
    token = load_token()

    protocol_id = create_protocol(token)
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
    for index, section in enumerate(PROCEDURE_SECTIONS):
        section_id = add_section(token, protocol_id, section["name"], index + 3)
        remove_empty_text_elements(token, section_id)
        for element in section["elements"]:
            add_element(token, section_id, element)

    # Reference manuals: upload the PDFs to the protocol, then show them in an attachments element
    section_id = add_section(token, protocol_id, "Reference manuals", len(PROCEDURE_SECTIONS) + 3)
    remove_empty_text_elements(token, section_id)
    element_id = add_element(token, section_id, {"element_type": "attachments", "name": "Thermo Fisher user guides", "data": ""})
    protocol_uuid = api("GET", f"protocols/{protocol_id}", token)["uuid"]
    for filename, url, description in MANUALS:
        attachment_id = upload_manual(token, protocol_uuid, filename, url, description)
        api("PUT", f"attachments/{attachment_id}", token, {"item": {"element_id": element_id}})

    print(f"\nDone: {SERVER_BASE}/knowledge/protocols/{protocol_id}")


if __name__ == "__main__":
    main()
