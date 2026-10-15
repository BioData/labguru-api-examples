import requests
import os
import json

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get("LABGURU_TOKEN")
server_base = (
    input("Enter server base (e.g., https://my.labguru.com): ")
    or "http://localhost:3000"
).rstrip("/")

# The protocol to tag and the tag label (comma-separated for multiple tags)
protocol_id = input("Enter the protocol ID: ")
tag = input("Enter the tag name: ")

# API URL for adding a tag
tags_url = f"{server_base}/api/v1/tags"

# Protocols are tagged with class_name "Knowledgebase::Protocol"
tag_data = {
    "token": token,
    "item": {
        "tag": tag,
        "class_name": "Knowledgebase::Protocol",
        "item_id": protocol_id,
    },
}

headers = {"Content-Type": "application/json"}

response = requests.post(tags_url, headers=headers, data=json.dumps(tag_data))

if response.status_code in (200, 201):
    print(f"Protocol {protocol_id} tagged with '{tag}'.")
    print("Response:", response.text)
else:
    print(f"Failed to tag protocol {protocol_id}. Status: {response.status_code}")
    print("Response:", response.text)
