import requests
import os
import json

BASE_URL = 'https://my.labguru.com/api/v1'
TOKEN = ""
def login(username,password):
  url = BASE_URL + "/sessions.json"
  data = {"login": username,"password": password}
  resp = requests.post(url, json=data)
  return resp.json()['token']

def add_project(name):
  url = BASE_URL + "/projects.json"
  data = {"item": {"title": name},"token": TOKEN}
  project = requests.post(url, json=data)
  return project.json()

def add_folder(project_id,name):
  url = BASE_URL + "/milestones.json"
  data = {"item": {"project_id": project_id,"title": name},"token": TOKEN}
  folder = requests.post(url, json=data)
  return folder.json()

def add_experiment(project_id,folder_id,name):
  url = BASE_URL + "/experiments.json"
  data = {"item": {"project_id": project_id, "milestone_id": folder_id, "title": name},"token": TOKEN}
  experiment = requests.post(url, json=data)
  return experiment.json()

def add_section(experiment_id, name):
  url = BASE_URL + "/sections.json"
  data = {"item": {"experiment_id": experiment_id, "name": name, "container_id": experiment_id, "container_type": "Projects::Experiment"},"token": TOKEN}
  section = requests.post(url, json=data)
  return section.json()

def add_empty_plate(experiment_id,section_id,cols,rows,name):
  url = BASE_URL + "/elements.json"
  data ={
	"item":  {
    "name": name,
    "element_type": "plate",
    "container_type": "ExperimentProcedure",
    "container_id": section_id,
    "rows": rows,
    "cols": cols,
    "experiment_id": experiment_id
    },"token": TOKEN
  }
  element = requests.post(url, json=data)
  return element.json()

def add_layer_data_to_plate(plate_id,filepath):
  url = BASE_URL + "/plates/" + str(plate_id) + "/update_layer?token=" + TOKEN
  print(url)
  f = open(filepath, "rb")
  response = requests.put(url, files= {"file": f})
  return response

def convert_plate_xls_to_json(xlsx_filepath,container_id):
  url = BASE_URL + "/elements/convert_xlsx_to_json?token=" + TOKEN + "&exp_pro_container_id=" + str(container_id)
  print(url)
  f = open(xlsx_filepath, "rb")
  response = requests.post(url, files= {"file_name[0]": f})
  #update plate data with the response
  print(response)
  plate_data = response.json()
  plate_json = json.dumps(plate_data["data"])
  file = open("data/json.txt","w")
  file.write(plate_json)
  file.close
  return plate_json

def update_plate(plate_id,plate_data):
  url = BASE_URL + "/elements/" + str(plate_id) + "?token=" + TOKEN
  print(url)
  plate_data = {"element": plate_data}
  response = requests.put(url, json=plate_data)
  return response.json()

def download_plate_xlsx(plate_id,filename):
  url = BASE_URL + "/elements/" + str(plate_id) + "/export_plate_to_xlsx_file.json?token=" + TOKEN
  print(url)
  response = requests.get(url)
  print(filename)
  file = open(filename, "wb")
  file.write(response.content)
  file.close()

def clone_plate(plate_id,names):
  url = BASE_URL + "/plates/" + str(plate_id) + "/duplicate?token=" + TOKEN
  print(url)
  response = requests.post(url, json = {"names": ["A","B","C"]})
  print(response.status_code)
  data = response.json()
  return data

def register(klass,filepath):
  print("TBD")
  return [] #to be implementd

def add_sample_element(a,b,c):
  print("TBD")
  return [] #to be implementd
