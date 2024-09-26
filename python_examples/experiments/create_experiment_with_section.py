import requests
import os
import json

#
# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
server_base = input("Enter server base (e.g., https://my.labguru.com/): ") or "http://localhost:3000"

url = f"{server_base}/api/v1/cell_lines?token={token}"

# Prepare the payload with the cell line details
data = {
    'item': {
        'name': 'HeLa',
        'organism': 'Human',
        'tissue': 'Cervix (cancer)',
        'medium_and_serum': 'DMEM with 10% FBS',
        'description': 'HeLa cell line for cancer research',
        # Add any other relevant fields here
    }
}

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a POST request to create the cell line
response = requests.post(url, headers=headers, data=json.dumps(data))

# Output the status and response from the server
print("\nCreating Cell Line...")
print("Status Code:", response.status_code)
if response.status_code == 201:
    cell_line = response.json()
    print("Cell line created successfully.")
    print("Cell Line ID:", cell_line['id'])
else:
    print("Failed to create the cell line.")
    print("Response:", response.json())
    exit()

# Construct the API URL
url = f"{server_base}/api/v2/experiments"

cell_line_id = cell_line['id']

# Prepare the payload with the experiment details
data = {
    "token": token,
    "item": {
        "title": "Investigating the Induction of Apoptosis by Curcumin in HeLa Cells",
        "project_id": 3,  # Replace with the actual project ID
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
                        "data": "Curcumin, a bioactive compound found in turmeric, has been reported to exhibit anti-cancer properties, including the induction of apoptosis in various cancer cell lines. <br> Understanding its mechanism in HeLa cells (a widely used human cervical cancer cell line) could contribute to developing novel therapeutic strategies against cervical cancer."
                    }
                ]
            }, 
            { "title": "Materials and Reagents",
             "elements": [
                    {
                        "element_type": "samples",
                        "data": json.dumps({
                        "item_class": "Biocollections::CellLine",
                        "item_id": cell_line_id,
                        "generic_collection_id": None
                    })
                }
            ],
        }
    ]}}

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a POST request to create the experiment
response = requests.post(url, headers=headers, data=json.dumps(data))

# Output the status and response from the server
print("Status Code:", response.status_code)
if response.status_code == 201:
    print("Experiment created successfully.")
    print("Response:", response.json())
else:
    print("Failed to create the experiment.")
    print("Response:", response.json())
