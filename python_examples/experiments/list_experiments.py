#pip install requests
import requests
base = 'https://my.labguru.com/api/v1/'
url = base + "sessions.json"
print url
resp = requests.post(url, {"login": "YOUREMAIL", "password": "YOURPASSWORD"})
token = resp.json()['token']
print token
#use the token to get data from the system
url = base + "/experiments.json?token=" + token
experiments = requests.get(url)
for experiment in experiments.json():
  print('{} {}'.format(experiment['id'], experiment['name']))
