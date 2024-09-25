import requests
import os

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get('LABGURU_TOKEN')
server_base = input("Enter server base (e.g., https://my.labguru.com/): ") or "http://localhost:3000"

# Get the Event ID to delete
event_id = input("Enter the Event ID to delete: ")

# Construct the API URL with the token as a query parameter
url = f"{server_base}/api/v1/events/{event_id}?token={token}"

# Set the headers for the request
headers = {'Content-Type': 'application/json'}

# Send a DELETE request to delete the event
response = requests.delete(url, headers=headers)

# Output the status and response from the server
print("Status Code:", response.status_code)
if response.status_code == 204:
    print("Event deleted successfully.")
else:
    print("Failed to delete the event.")
    print("Response:", response.json())