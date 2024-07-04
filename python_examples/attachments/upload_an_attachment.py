from requests_toolbelt import MultipartEncoder
import requests
import json

base =  'https://my.labguru.com'

# Get a token:
url = base + '/api/v1/sessions.json'
params = {'login': EMAIL, 'password': PASSWORD}
r = requests.post(url, params)
js =  json.loads(r.text)
token = str(js["token"])

# Upload the attachment file:
url = base + "/api/v1/attachments.json"
file_location = "/Users/liron/Documents/Screening/ValidationPlate_MASTER.sdf"
m_fields = { 'item[attachment]': ('ValidationPlate_MASTER.sdf', open(file_location, "rb"), 'application/vnd.Kinar'), 
             'item[title]': 'Importing compounds', 
             'token' : token}
m = MultipartEncoder(m_fields)
r = requests.post(url, data = m, headers={ 'Content-Type': m.content_type } )
js =  json.loads(r.text)
attachment_id = str(js["id"])
