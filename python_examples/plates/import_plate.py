import requests
import os
import json
token = raw_input("Enter token:") or os.environ.get('LABGURU_TOKEN')
server_base = raw_input("Enter sever base (eg: https://my.labguru.com/ no API section needed") or "http://localhost:3000"
url = server_base  + "/api/v1/elements?token=" + token
container_id = raw_input("Enter Container ID") or 196
print "Creating a plate element"
item_data = { "item":{
	 "name":"Imported Plate",
	 "element_type":"plate",
	 "data":"{\"wells\":[],\"samples\":[],\"added_samples\":[],\"properties\":[],\"control_annotation_hidden\":false}",
	 "container_type":"ExperimentProcedure",
     "cols": 12,
     "rows": 8,
	 "container_id":container_id, "description":""},
	"element":{}}

print item_data
x = requests.post(url, json = item_data)
plate_json =  x.json()
plate_id = plate_json["id"]
print(plate_json)
print(plate_id)
filepath = raw_input("Enter path to the excel file to import") or "labguru_plate_import_template.xlsx"

#convert xlsx to plate json
url = server_base + "/api/v1/elements/convert_xlsx_to_json?token=" + token
print(url)
f = open(filepath, "rb")
response = requests.post(url, files= {"file_name[0]": f, "exp_pro_container_id": container_id})

#update plate data with the response
plate_data = response.json()
plate_json["data"] = json.dumps(plate_data["data"])
item_data = {"element": plate_json}

plate_id = str(plate_id)
url = server_base + "/api/v1/elements/" + plate_id + "?token=" + str(token)
print(url)
response = requests.put(url, json = item_data)
print(response.status_code)
