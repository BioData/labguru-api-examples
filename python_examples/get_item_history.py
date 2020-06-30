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

# Get the history of an item (in this example a sequence with id 27):
item_params = '{"object_id":"27", "object_type":"Biocollections::Sequence"}'
histories_url = str(base + "histories.json?token=" + token + "&filter=" + item_params)
item_histories = requests.get(histories_url)
history =  json.loads(item_histories.text)
