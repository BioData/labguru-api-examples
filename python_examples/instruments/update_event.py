import requests
import os
import json
from datetime import datetime, timedelta

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
server_base = input("Enter server base (e.g., https://my.labguru.com/): ") or "http://localhost:3000"

# Get the Event ID to update
event_id = input("Enter the Event ID to update: ")

# Construct the API URL with the token as a query parameter
url = f"{server_base}/api/v1/events/{event_id}?token={token}"

# Get the current time and calculate the new end time (e.g., extend the event by 1 hour)
now = datetime.now()
start_date = now.strftime('%Y-%m-%d %H:%M:%S')
end_time = now + timedelta(hours=3)  # Extend the event to end 3 hours from now
end_date = end_time.strftime('%Y-%m-%d %H:%M:%S')

# Prepare the payload with the updated event details
data = {
    'item': {
        'name': 'Updated Lab Meeting',
        'start_date': start_date,
        'end_date': end_date,
        'description': 'Updated description for the meeting',
        'notify_members': '[0]',  # Options: '[1]' for only me, '[-1]' for all participants, '[0]' for none
        'notify_at': start_date,  # Notify at the start of the event
        'is_fullday_event': False,
        'eventable_id': event_id,  # Replace with the actual instrument ID if changing
        'eventable_type': 'System::Instrument'
    }
}

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a PUT request to update the event
response = requests.put(url, headers=headers, data=json.dumps(data))

# Output the status and response from the server
print("Status Code:", response.status_code)
if response.status_code == 200:
    print("Event updated successfully.")
    print("Response:", response.json())
else:
    print("Failed to update the event.")
    print("Response:", response.json())