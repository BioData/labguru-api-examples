import requests
import os
import json

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
server_base = input("Enter server base (e.g., https://my.labguru.com/): ") or "http://localhost:3000"

# Construct the API URL with the token as a query parameter
url = f"{server_base}/api/v1/instruments?token={token}"

# Prepare the payload with all necessary instrument details
data = {
    'item': {
        'name': 'RT-PCR',
        'model_number': 'EQ-123',
        'serial_number': 'SE-12',
        'equipment_type': 'Type A',
        'manufacturer': 'Thermo Fisher',
        'purchase_date': '2020-01-01',
        'warranty_expired': '2022-01-01',
        'maintenance_information': 'General maintenance info',
        'description': 'RT-PCR machine for DNA amplification',
    }
}

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a POST request to create the instrument
response = requests.post(url, headers=headers, data=json.dumps(data))

# Output the status and response from the server
print("Status Code:", response.status_code)
print("Response:", response.json())

