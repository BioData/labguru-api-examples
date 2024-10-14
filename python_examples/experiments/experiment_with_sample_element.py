import requests
import os
import json

def get_token_and_server_base():
    token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
    server_base = (
    input("Enter server base (e.g., https://my.labguru.com/): ") or os.getenv('LABGURU_SERVER_BASE', 'https://my.labguru.com/'))
    return token, server_base

def create_cell_line(token, server_base):
    url = f"{server_base}/api/v1/cell_lines?token={token}"
    data = {
        'item': {
            'name': 'HeLa',
            'organism': 'Human',
            'tissue': 'Cervix (cancer)',
            'medium_and_serum': 'DMEM with 10% FBS',
            'description': 'HeLa cell line for cancer research',
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("\nCreating Cell Line...")
    print("Status Code:", response.status_code)
    if response.status_code == 201:
        cell_line = response.json()
        print("Cell line created successfully.")
        print("Cell Line ID:", cell_line['id'])
        return cell_line['id']
    else:
        print("Failed to create the cell line.")
        print("Response:", response.json())
        exit()

def create_experiment(token, server_base, cell_line_id):
    url = f"{server_base}/api/v2/experiments"
    data = {
        "token": token,
        "item": {
            "title": "Investigating the Induction of Apoptosis by Curcumin in HeLa Cells",
            "project_id": 71,
            "milestone_name": "objective",
            "sections": [
                {
                    "title": "Objective ",
                    "elements": [
                        {
                            "element_type": "text",
                            "data": "To determine the effect of curcumin on inducing apoptosis in HeLa cells and to elucidate the apoptotic pathways involved."
                        }
                    ]
                },
                {
                    "title": "Background",
                    "elements": [
                        {
                            "element_type": "text",
                            "data": "Curcumin, a bioactive compound found in turmeric, has been reported to exhibit anti-cancer properties, including the induction of apoptosis in various cancer cell lines. Understanding its mechanism in HeLa cells (a widely used human cervical cancer cell line) could contribute to developing novel therapeutic strategies against cervical cancer."
                        }
                    ]
                }, 
                {"title": "Materials and Reagents",
                 "elements": [
                        {
                            "element_type": "samples",
                            "data": ""
                    }
                ],
            }
        ]}}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def create_sample(token, server_base, cell_line_id, element_id):
    payload = {
        "token": token,
        "item": {
            "container_type": 'Element',
            "container_id": element_id,
            "item_id": cell_line_id,
            "item_type": "Biocollections::CellLine",
            "generic_collection_id": None
        }
    }
    response = requests.post(
        url=f"{server_base}/api/v1/samples.json",
        json=payload
    )
    return response.json()

def update_element(token, server_base, element_id, material_sample, sample_response):
    item_data = material_sample.get('item', {})
    print(item_data);
    material_sample_template = {
        'selected_stocks': [],
        'storages': [],
        'id': material_sample['id'],
        'name': item_data.get('name', 'Unnamed Sample'),
        'organism': 'Human',
        'url': item_data.get('url'),
        'collection_name': "Cell Lines",
        'data': sample_response,
        'remarks': None,
        'item': {
            'item_class': "Biocollections::CellLine",
            'item_id': material_sample['id'],
            'generic_collection_id': None
        },
        'container': {
            'type': 'Element', 'id': element_id
        },
        'generic_id': None,
        'stocks': [],
        'properties': [],
        'saved_stocks_ids': [],
        'select_all_stocks': False
    }

    materials_element_template = {
        'properties': [],
        'headers': {
            'Cell Lines': [
                {'header': 'Organism', 'attribute': 'organism'},
                {'header': 'Medium and serum', 'attribute': 'medium_and_serum'},
                {'header': 'Source', 'attribute': 'source'},
                {'header': 'Tissue', 'attribute': 'tissue'},
                {'header': 'SysID', 'attribute': 'auto_name'}
            ]
        },
        'samples': [material_sample_template]
    }

    url = f"{server_base}/api/v1/elements/{element_id}"
    headers = {"accept": "*/*", "Content-Type": "application/json"}
    payload = {"token": token, "data": json.dumps(materials_element_template)}
    response = requests.put(url, headers=headers, json=payload)
    return response

def main():
    token, server_base = get_token_and_server_base()
    cell_line_id = create_cell_line(token, server_base)
    experiment_response = create_experiment(token, server_base, cell_line_id)
    element_id = experiment_response['experiment_procedures'][2]['experiment_procedure']['elements'][0]['id']
    sample_response = create_sample(token, server_base, cell_line_id, element_id)
    material_sample = sample_response  # Assuming material_sample is the same as sample_response
    update_element(token, server_base, element_id, material_sample, sample_response)

if __name__ == "__main__":
    main()