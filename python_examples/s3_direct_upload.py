"""Uses Labguru API to get an auth token and add a file attachment given the path to the file
"""
import os
import requests
import sys
from urllib.parse import unquote


if len(sys.argv) > 1:
    path = sys.argv[1]
    filename = os.path.basename(path)
else:
    print("Please provide a filename as a command-line argument.")
    sys.exit(1)

API_BASE = "SERVER"
LOGIN = "EMAIL"
PASSWORD = "PASSWORD"
CONTENT_TYPE = "application/octet-stream"
UUID = "UUID"
ATTACHABLE_TYPE = "TYPE"
# get your token
try:
    token_request = requests.post(
        os.path.join(API_BASE, "api/v1/sessions.json"),
        json={"login": LOGIN, "password": PASSWORD},
    )
    token_request.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


token = token_request.json()["token"]
try:
    data = {
        "item": {
            "title": filename,
            "attachment": {
                "original_filename": filename,
                "content_type": CONTENT_TYPE,
            },
            "attach_to_uuid": UUID,
            "attachable_type": ATTACHABLE_TYPE,
        },
        "token": token,
    }

    attachment_response = requests.post(
        os.path.join(API_BASE, "api/v2/attachments/s3_direct_upload"), json=data
    )

    attachment_response.raise_for_status()

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

print(attachment_response.status_code)
if (attachment_response.status_code != 200):
    print(attachment_response.content)
    exit(1)

json = attachment_response.json()
url = json["presigned_url"]
data_to_upload = open(path, "rb")  # Open the file in binary mode
upload_response = requests.put(url, data=data_to_upload)

# Check if the upload was successful
if upload_response.status_code == 200:
    print("File uploaded successfully.")
else:
    print(upload_response.content)
    print(f"Failed to upload file, status code: {upload_response.status_code}")
