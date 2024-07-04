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
NUMBER_OF_PARTS = 10
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
        "parts": NUMBER_OF_PARTS,
        "token": token,
    }

    attachment_response = requests.post(
        os.path.join(API_BASE, "api/v2/attachments/s3_multipart_upload"), json=data
    )

    attachment_response.raise_for_status()

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

print(attachment_response.status_code)
if (attachment_response.status_code != 200):
    print(attachment_response.content)
    exit(1)
json = attachment_response.json()
urls = json["urls"]
upload_id = json["upload_id"]
attachment_id = json["id"]


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def split_file(file_path, num_parts):
    filesize = os.path.getsize(file_path)
    chunk_size = filesize // num_parts

    with open(file_path, "rb") as f:
        for i in range(num_parts):
            yield f.read(chunk_size)


def upload_parts(file_path, presigned_urls):
    parts = list(split_file(file_path, len(presigned_urls)))
    part_num = 0
    etags = []
    printProgressBar(part_num, len(parts), prefix = "Upload:", suffix = "complete")
    for url, part in zip(presigned_urls, parts):
        part_num += 1
        res = requests.put(url, data=part)
        if res.status_code != 200:
            raise Exception(
                f"Upload failed for part: {part}, status code: {res.status_code}"
            )
        etags.append(res.headers["ETag"])
        printProgressBar(part_num, len(parts), prefix = "Upload:", suffix = "complete")

    return etags


def complete_upload(etags):
    data = {"etags": etags, "token": token, "upload_id": upload_id, "id": attachment_id}
    print(etags)
    response = requests.post(
        os.path.join(API_BASE, "api/v2/attachments/s3_multipart_finished"), json=data
    )
    if response.status_code != 200:
        print(response.content)
        raise Exception("Failed to complete the multipart upload")


# replace with your file path and presigned urls

etags = upload_parts(path, urls)
complete_upload(etags)
