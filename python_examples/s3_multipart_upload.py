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

API_BASE = "http://localhost:3000/"
LOGIN = "EMAIL"
PASSWORD = "PASSWORD"
CONTENT_TYPE = "application/octet-stream"

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
            "title": "My Attachment",
            "attachment": {
                "original_filename": filename,
                "content_type": CONTENT_TYPE,
            },
        },
        "token": token,
    }

    attachment_request = requests.post(
        os.path.join(API_BASE, "api/v2/attachments/s3_multipart_upload"), json=data
    )

    attachment_request.raise_for_status()

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

print(attachment_request.status_code)
json = attachment_request.json()
urls = json["urls"]
upload_id = json["upload_id"]
attachment_id = json["id"]


def split_file(file_path, num_parts):
    filesize = os.path.getsize(file_path)
    chunk_size = filesize // num_parts

    with open(file_path, "rb") as f:
        for i in range(num_parts):
            yield f.read(chunk_size)


def upload_parts(file_path, presigned_urls):
    parts = list(split_file(file_path, len(presigned_urls)))
    etags = []

    for url, part in zip(presigned_urls, parts):
        res = requests.put(url, data=part)
        if res.status_code != 200:
            raise Exception(
                f"Upload failed for part: {part}, status code: {res.status_code}"
            )
        etags.append(res.headers["ETag"])

    return etags


def complete_upload(etags):
    data = {"etags": etags, "token": token, "upload_id": upload_id, "id": attachment_id}
    print(etags)
    response = requests.post(
        os.path.join(API_BASE, "api/v2/attachments/s3_multipart_finished"), json=data
    )
    if response.status_code != 200:
        raise Exception("Failed to complete the multipart upload")


# replace with your file path and presigned urls

etags = upload_parts(path, urls)
complete_upload(etags)
