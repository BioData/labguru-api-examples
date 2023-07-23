"""Uses Labguru API to get an auth token and add a file attachment given the path to the file
"""
import os

import requests

API_BASE = 'https://mycompany.labguru.com/api/v1/'
FILE_PATH = '/path/to/my_attachment.pdf'  # absolute path
LOGIN = 'user@email.com'
PASSWORD = 'mypass'

# get your token
token_request = requests.post(
    os.path.join(API_BASE, 'sessions.json'), json={'login': LOGIN, 'password': PASSWORD}
)

token = token_request.json()['token']

# read file into memory
with open(FILE_PATH, 'rb') as f:
    attachment = f.read()

attachment_request = requests.post(
    os.path.join(API_BASE, 'attachments'),
    data={'item[title]': 'My Attachment', 'item[attach_to_uuid]': target_uuid, 'token': token},
    files={'item[attachment]': ('my_attachment.pdf', attachment)},
)

print(attachment_request.status_code)
