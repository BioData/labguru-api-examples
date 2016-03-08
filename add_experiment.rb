#see https://github.com/rest-client/rest-client
#this code can be adpated to any other rest client. 
require 'rest-client'
require 'json'
#if you are using a private cloud / local install you will need to use a different url. 
#base = "https://api.labguru.com"

#1. Get a token
url = base + "/api/v1/sessions.json"
params = {login: "EMAIL",password: "PASSWORD"}
response = JSON.parse(RestClient.post(url,params))
token = response["token"]

#2. Add a project
url = base + "/api/v1/projects.json"
params = {
  item: { 
    title: "FtsH function in Chloroplasts",
    description: "As FtsH regulates the levels of both LpxC and KdtA it is required for synthesis of both the protein and lipid components of lipopolysaccharide (LPS)."
  }, 
  token: token
}
response =  JSON.parse(RestClient.post(url,params))
project_id = response["id"]

#3. Add a milestone
url = base + "/api/v1/milestones.json"
params = {
  item: { 
    title: "FtsH Clonning to PBR322",
    description: "Cloning and Sequencing to ensure correct targets",
    project_id: project_id
  }, 
  token: token
}
response =  JSON.parse(RestClient.post(url,params))
milestone_id = response["id"]

#4. Add an experiment to a milestone

url = base + "/api/v1/experiments.json"
params = {
  item: { 
    title: "Total DNA Extraction of Genomic DNA",
    description: "Extraction of DNA from N.Tabbacum, before picking the FtsH gene",
    project_id: project_id,
    milestone_id: milestone_id
  }, 
  token: token
}
response =  JSON.parse(RestClient.post(url,params))
experiment_id = response["id"]
experiment_uuid = response["uuid"]

#5. Add a note to expeiment 
url = base + "/api/v1/elements.json"
params = {
  item: { 
    data: "Plants are look weird - I'm repeating this experiment",
    element_type: "text",
    container_type: "Projects::Experiment",
    container_id: experiment_id,
    field_name: "notes"
  }, 
  token: token
}
response =  JSON.parse(RestClient.post(url,params))
note_id = response["id"]


#6. Add an attachment to an experiment 
url = base + "/api/v1/attachments.json"
params = {
  item: {
   title: "Sequencing Results",
   description: "As recieved from IDT",
   attachment: File.open("/Users/admin/Desktop/data2.seq","r"),
   attach_to_uuid: experiment_uuid
  },
  token: token
}
response =  JSON.parse(RestClient.post(url,params))
