import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import sys

# Load the dataset from a CSV file
# Get the file path from command line arguments
file_path = sys.argv[1]

# Retrieve the API endpoint and API key from environment variables
base_api_endpoint = os.getenv("LABGURU_SERVER")
api_key = os.getenv("LABGURU_TOKEN")
api_endpoint = f"{base_api_endpoint}/api/v1/datasets"

# Step 1: Upload the attachment

url = f"{base_api_endpoint}/api/v1/attachments.json"


multipart_data = MultipartEncoder(
    fields={
        "item[title]": "IMG_0365",
        "item[description]": "File uploaded via API",
        "item[attachment]": (
            os.path.basename(file_path),
            open(file_path, "rb"),
            "image/jpeg",
        ),
        "token": api_key,
    }
)

headers = {"Content-Type": multipart_data.content_type}

response = requests.post(url, data=multipart_data, headers=headers)
response_data = response.json()


attachment_id = response_data["id"]
print(f"Attachment ID: {attachment_id}")

# Step 2: Post to dataset API
dataset_url = f"{base_api_endpoint}/api/v1/datasets"
dataset_params = {
    "item": {"name": "DATASET NAME", "data_attachment_id": attachment_id},
    "token": api_key,
}

dataset_response = requests.post(
    dataset_url, json=dataset_params, headers={"Authorization": f"Token {api_key}"}
)
dataset_response_data = dataset_response.json()

print(dataset_response_data)
