import requests
import os
import json

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get("LABGURU_TOKEN")
server_base = (
    input("Enter server base (e.g., https://my.labguru.com): ")
    or "http://localhost:3000"
).rstrip("/")

# Inventory items are tagged by their class name, for example:
#   Biocollections::Antibody, Biocollections::Plasmid, Biocollections::Bacterium,
#   Biocollections::Tissue
class_name = (
    input("Enter the item class name (default Biocollections::Antibody): ")
    or "Biocollections::Antibody"
)
item_id = input("Enter the item ID: ")
tag = input("Enter the tag name: ")

# API URL for adding a tag
tags_url = f"{server_base}/api/v1/tags"

tag_data = {
    "token": token,
    "item": {
        "tag": tag,
        "class_name": class_name,
        "item_id": item_id,
    },
}

headers = {"Content-Type": "application/json"}

response = requests.post(tags_url, headers=headers, data=json.dumps(tag_data))

if response.status_code in (200, 201):
    print(f"{class_name} {item_id} tagged with '{tag}'.")
    print("Response:", response.text)
else:
    print(f"Failed to tag {class_name} {item_id}. Status: {response.status_code}")
    print("Response:", response.text)
