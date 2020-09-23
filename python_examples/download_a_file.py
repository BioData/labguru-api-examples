# 1. Get the token
# 2. Get the attachment details
# 3. Use the attachment details to know the file name
# 4. Perform a get request to attachment download and pour the answer into a temp file

import requests
base = 'https://my.labguru.com/api/v1/'

# 1. Get the token
url = base + "sessions.json"
print url

resp = requests.post(url, {"login": "YOUREMAIL", "password": "YOURPASSWORD"})
token = resp.json()['token']
print token

# 2. Get the attachment details
attachment_url = base + "attachments/"+ str(ATTACHMENT_ID) +".json?token=" + token
response = requests.get(attachment_url)
attachment = json.loads(response.text)

# 3. Use the attachment details to know the file name
file_name = attachment["attachment_file_name"]
file_location = "/Users/liron/Downloads/" + file_name

# 4. Perform a get request to attachment download and pour the answer into a temp file
download_url = base + "attachments/" + str(ATTACHMENT_ID) +  "/download.json?token=" + token
response = requests.get(download_url, allow_redirects=True)
open(file_location, 'wb').write(response.content)
