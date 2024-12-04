import csv
import json
import requests
from typing import List, Dict, Any

# Constants for the API key and URL (replace with your actual values)
API_KEY = "TOKEN"
API_URL = "https://my.labguru.com/api/v1"
SECTION_ID = "4369"  # Replace with the actual section ID


class CsvRecord:
    def __init__(
        self, field_name: str, field_type: str, min_value: str, max_value: str, hint: str, row: int, readonly: bool
    ):
        self.field_name = field_name
        self.field_type = field_type
        self.min_value = min_value
        self.max_value = max_value
        self.hint = hint
        self.row = row
        self.readonly = readonly


def read_structure_file(file_path: str) -> List[CsvRecord]:
    """Reads the structure CSV file and returns a list of CsvRecord objects."""
    records = []
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                CsvRecord(
                    field_name=row.get("field_name", ""),
                    field_type=row.get("type", ""),
                    min_value=row.get("min", ""),
                    max_value=row.get("max", ""),
                    hint=row.get("hint", ""),
                    row=int(row.get("row", 0)),
                    readonly=row.get("readonly", "").lower() == "true",
                )
            )
    return records


def read_samples_file(file_path: str) -> List[Dict[str, str]]:
    """Reads the samples CSV file and returns a list of dictionaries."""
    samples = []
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            samples.append(row)
    return samples


def generate_html_table(structure: List[CsvRecord], samples: List[Dict[str, str]]) -> str:
    """Generates an HTML table based on the structure and samples."""
    html = ["<table style='width: 100%; border-collapse: collapse;' border='1'>"]

    # Add table header
    html.append("<thead><tr>")
    for record in structure:
        if record.field_name:  # Only add columns that should be displayed
            html.append(f"<th style='padding: 8px; text-align: left;'>{record.field_name}</th>")
    html.append("</tr></thead>")

    # Add table body
    html.append("<tbody>")

    # Add a row for each sample
    for sample in samples:
        html.append("<tr>")
        for record in structure:
            value = sample.get(record.field_name, "")
            print(record.field_type, record.field_name, value, record.field_type == "hidden")
            if record.field_type == "hidden":
                # Special case: Add hidden input and string representation for sample_id
                html.append(
                    f"<td style='padding: 8px;'>"
                    f"<input type='hidden' name='{record.field_name}' value='{value}'>"
                    f"{value}</td>"
                )
            else:
                # Regular inputs
                readonly_attr = "readonly" if record.readonly else ""
                display_attr = "style='display: none;'" if not record.field_type or record.field_type == "hidden" else ""
                html.append(
                    f"<td style='padding: 8px;' {display_attr}>"
                    f"<input class='form-control' name='{record.field_name}' type='{record.field_type}' "
                    f"placeholder='{record.hint}' "
                    f"{f'min=\"{record.min_value}\"' if record.field_type == 'number' and record.min_value else ''} "
                    f"{f'max=\"{record.max_value}\"' if record.field_type == 'number' and record.max_value else ''} "
                    f"value='{value}' {readonly_attr}></td>"
                )
        html.append("</tr>")

    # Close the table body
    html.append("</tbody></table>")

    return "".join(html)



def add_form_element(section_id: str, html_table: str):
    form_element = {
        "item": {
            "name": "Sample Manager",
            "element_type": "form",
            "data": html_table,
            "settings": '{"out_of_range":"allow","allow_row_toggle":true}',
            "container_type": "ExperimentProcedure",
            "container_id": section_id,
            "is_valid": False,
        }
    }
    response = requests.post(f"{API_URL}/elements?token={API_KEY}", json=form_element)
    if response.status_code == 201:
        print("Form element added successfully.")
    else:
        print(f"Error: {response.status_code}, Details: {response.text}")


def main(structure_file_path: str, samples_file_path: str):
    structure = read_structure_file(structure_file_path)
    samples = read_samples_file(samples_file_path)
    print(samples)
    html_table = generate_html_table(structure, samples)
    print(html_table)  # For demonstration, print the generated table
    secion_id = "123"  # Replace with the actual section ID
    add_form_element(SECTION_ID, html_table)

# Call main with the CSV file path
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide the CSV file path as an argument.")
    else:
        main(sys.argv[1], sys.argv[2])
