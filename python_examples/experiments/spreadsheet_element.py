import requests
import os
import json


def get_token_and_base():
    token = input("Enter token: ") or os.environ.get("LABGURU_TOKEN")
    base_url = (
        input("Enter server base (e.g., https://my.labguru.com/api/v1): ")
        or "http://localhost:3000/api/v1"
    )
    return token, base_url


def safe_json_response(response):
    try:
        return response.json()
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Response text:", response.text)
        return None


def add_experiment(project_id, folder_id, name, token, base_url):
    url = f"{base_url}/experiments.json"
    data = {
        "item": {"project_id": project_id, "milestone_id": folder_id, "title": name},
        "token": token,
    }
    experiment = requests.post(url, json=data)
    return safe_json_response(experiment)


def add_section(experiment_id, name, token, base_url):
    url = f"{base_url}/sections.json"
    data = {
        "item": {
            "experiment_id": experiment_id,
            "name": name,
            "container_id": experiment_id,
            "container_type": "Projects::Experiment",
        },
        "token": token,
    }
    section = requests.post(url, json=data)
    return safe_json_response(section)


def get_static_spread_data():
    return {
        "version": "16.1.4",
        "sheetCount": 1,
        "customList": [],
        "sheets": {
            "Sheet1": {
                "name": "Sheet1",
                "isSelected": True,
                "visible": 1,
                "frozenTrailingRowStickToEdge": True,
                "frozenTrailingColumnStickToEdge": True,
                "theme": "Office",
                "data": {"defaultDataNode": {"style": {"themeFont": "Body"}}},
                "rowHeaderData": {"defaultDataNode": {"style": {"themeFont": "Body"}}},
                "colHeaderData": {"defaultDataNode": {"style": {"themeFont": "Body"}}},
                "selections": {
                    "0": {"row": 0, "col": 0, "rowCount": 1, "colCount": 1},
                    "length": 1,
                },
                "rowOutlines": {"items": []},
                "columnOutlines": {"items": []},
                "cellStates": {},
                "states": {},
                "outlineColumnOptions": {},
                "autoMergeRangeInfos": [],
                "shapeCollectionOption": {"snapMode": 0},
                "printInfo": {
                    "bestFitRows": True,
                    "margin": {
                        "top": 5,
                        "bottom": 5,
                        "left": 5,
                        "right": 5,
                        "header": 30,
                        "footer": 30,
                    },
                    "paperSize": {"width": 850, "height": 1100, "kind": 1},
                },
                "index": 0,
                "order": 0,
            }
        },
        "sheetTabCount": 0,
        "namedPatterns": {},
        "pivotCaches": {},
    }


def create_spreadsheet_element(section_id, data_array, token, base_url):
    # Construct the JSON payload for the spreadsheet element
    spread_data = get_static_spread_data()
    spread_data["sheets"]["Sheet1"]["data"]["dataTable"] = {
        str(row_idx): {
            str(col_idx): {"value": value} for col_idx, value in enumerate(row)
        }
        for row_idx, row in enumerate(data_array)
    }

    url = f"{base_url}/elements.json"
    payload = {
        "item": {
            "container_id": section_id,
            "container_type": "ExperimentProcedure",
            "element_type": "excel",
            "data": json.dumps({"spread": json.dumps(spread_data), "height": 600}),
        },
        "token": token,
    }
    response = requests.post(url, json=payload)
    return safe_json_response(response)


def select_project():
    print("enter project id")
    project_id = input()
    return project_id


def select_folder():
    print("enter folder id")
    folder_id = input()
    return folder_id


def main():
    token, base_url = get_token_and_base()
    project_id = select_project()
    folder_id = select_folder()
    experiment_name = "Test Experiment"

    experiment = add_experiment(project_id, folder_id, experiment_name, token, base_url)
    experiment_id = experiment.get("id") if experiment else None

    if experiment_id:
        section_name = "Spreadsheet Section"
        section = add_section(experiment_id, section_name, token, base_url)
        section_id = section.get("id") if section else None

        if section_id:
            # Sample data array for spreadsheet
            data_array = [
                ["Sample Id", "Source", "Ph", "Color", "Weight"],
                ["A1", "Lab A", 7.2, "Red", 5.5],
                ["B1", "Lab B", 6.8, "Blue", 6.0],
            ]

            spreadsheet_element = create_spreadsheet_element(
                section_id, data_array, token, base_url
            )
            print("Spreadsheet element created:", spreadsheet_element)


if __name__ == "__main__":
    main()
