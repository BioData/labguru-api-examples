import requests
import os
import json
from datetime import datetime, timedelta

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
server_base = input("Enter server base (e.g., https://my.labguru.com/): ") or "http://localhost:3000"
instrument_id = input("Enter instrument ID: ") or "1"
# Construct the API URL with the token as a query parameter
url = f"{server_base}/api/v1/events?token={token}"

now = datetime.now()
start_date = now.strftime('%Y-%m-%d %H:%M:%S')
end_time = now + timedelta(hours=2)
end_date = end_time.strftime('%Y-%m-%d %H:%M:%S')
notify_date = now + timedelta(hours=-24)
notify_date = notify_date.strftime('%Y-%m-%d %H:%M:%S')

# Prepare the payload with all necessary event details
data = {
    'item': {
        'name': 'PCR Run',
        'start_date': start_date,
        'end_date': end_date,
        'description': 'DNA amplification for Bcl-2 gene',
        'notify_members': '[0]',  # Options: '[1]' for only me, '[-1]' for all participants, '[0]' for none
        'notify_at': notify_date,
        'is_fullday_event': True,
        'eventable_id': instrument_id,  # Replace with the actual instrument ID
        'eventable_type': 'System::Instrument'
    }
}

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a POST request to create the event
response = requests.post(url, headers=headers, data=json.dumps(data))

# Output the status and response from the server
print("Status Code:", response.status_code)
print("Response:", response.json())
