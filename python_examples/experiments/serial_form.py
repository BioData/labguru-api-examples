import csv
import json
import requests
from typing import List, Dict, Any

# Constants for the API key and URL (replace with your actual values)
API_KEY = "YOUR_API_KEY_HERE"
API_URL = "YOUR_API_URL_HERE"


class CsvRecord:
    def __init__(
        self, field_name: str, type: str, min: str, max: str, hint: str, row: int
    ):
        self.field_name = field_name
        self.type = type
        self.min = min
        self.max = max
        self.hint = hint
        self.row = row


def read_csv_file(file_path: str) -> List[CsvRecord]:
    records = []
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                CsvRecord(
                    field_name=row.get("field_name", ""),
                    type=row.get("type", ""),
                    min=row.get("min", ""),
                    max=row.get("max", ""),
                    hint=row.get("hint", ""),
                    row=int(row.get("row", 0)),
                )
            )
    return records


def generate_html_table(records: List[CsvRecord]) -> str:
    html = ["<table style='width: 100%;'><tbody>"]
    grouped_records = {}

    for record in records:
        grouped_records.setdefault(record.row, []).append(record)

    html.append("<tr>")
    for row_group in grouped_records.values():
        html.append(f"<td>'{record.field_name}' </td>")
    html.append("</tr>")
    html.append("<tr>")
    for row_group in grouped_records.values():
        for record in row_group:
            html.append(f"<td style='width: 25.0000%;'>{record.hint}</td>")
            html.append(
                f"<td style='width: 25.0000%;'><input disabled='' class='form-control' name='{record.field_name}' "
                f"title='Cannot add values to fields in protocols. To add values, start an experiment from the protocol' "
                f"type='{record.type}' placeholder='{record.field_name}' "
                f"{f'min=\"{record.min}\"' if record.type == 'number' and record.min else ''} "
                f"{f'max=\"{record.max}\"' if record.type == 'number' and record.max else ''}></td>"
            )
    html.append("</tr>")
    html.append("</tbody></table><p><br></p>")
    return "".join(html)


def generate_form_json(records: List[CsvRecord]) -> str:
    questions = []
    for record in records:
        question_data = []
        if record.min:
            question_data.append({"min": record.min})
        if record.max:
            question_data.append({"max": record.max})

        questions.append(
            {
                "question": record.field_name,
                "question_type": record.type,
                "question_data": question_data,
            }
        )

    form_json = {"form_json": {"questions": questions}}
    return json.dumps(form_json)


def add_protocol(protocol: Dict[str, Any]) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(f"{API_URL}/protocols", headers=headers, json=protocol)
    if response.status_code == 200:
        print("Protocol added successfully.")
        return response.json().get("id", "")
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")
        return ""


def add_procedure(procedure: Dict[str, Any], protocol_id: str) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(f"{API_URL}/sections", headers=headers, json=procedure)
    if response.status_code == 200:
        print("Procedure added successfully.")
        return response.json().get("id", "")
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")
        return ""


def add_form_element(section_id: str, html_table: str, form_json: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    form_element = {
        "item": {
            "name": "Sample Manager",
            "element_type": "form",
            "data": html_table,
            "settings": '{"out_of_range":"allow","allow_row_toggle":true}',
            "container_type": "ExperimentProcedure",
            "container_id": section_id,
            "description": form_json,
            "is_valid": False,
        }
    }
    response = requests.post(f"{API_URL}/elements", headers=headers, json=form_element)
    if response.status_code == 200:
        print("Form element added successfully.")
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")


def main(csv_file_path: str):
    csv_records = read_csv_file(csv_file_path)

    protocol = {"name": "New Protocol", "description": "This is a sample protocol"}
    protocol_id = add_protocol(protocol)

    if protocol_id:
        procedure = {
            "item": {
                "container_type": "Knowledgebase::Protocol",
                "container_id": protocol_id,
                "name": "Report Form",
                "position": 1,
            }
        }
        section_id = add_procedure(procedure, protocol_id)

        if section_id:
            html_table = generate_html_table(csv_records)
            form_json = generate_form_json(csv_records)
            add_form_element(section_id, html_table, form_json)


# Call main with the CSV file path
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide the CSV file path as an argument.")
    else:
        main(sys.argv[1])
