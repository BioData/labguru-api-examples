#add_attachments_section
require 'rest-client'
require 'json'
base = "https://my.labguru.com/api/v1"

#1. get a token
url = @base + "/api/v1/sessions.json"
params = {login: "EMAIL",password: "PASSWORD"}
response = JSON.parse(RestClient.post(url,params))
@token = response["token"]

#get the documents - to verify its existance
doc_id = 1 #<< hard coded change to the document you need
documents_url = "#{base}/documents/#{doc_id}.json?token=#{@token}"
response = JSON.parse(RestClient.get(documents_url))
document_uuid = response["uuid"]

#2. get the documents' first section (currently documents only have one section)
sections_url =  "#{base}/sections.json?filter={\"container_type\": \"Knowledgebase::AbstractDocument\", \"container_id\": #{doc_id}}&token=#{@token}"
response = JSON.parse(RestClient.get(sections_url))
section_id =  response.first["id"]

#3. upload a file
url = "#{base}/attachments.json"
params = {
  item: {
   title: "Plot",
   description: "Our result",
   attachment: File.open("/Users/jonathan/Desktop/plot.png","r"),
   attachable_type: 'Knowledgebase::AbstractDocument', #we cannot use attach_to_uuid and need to specify this explicitly.
   attachable_id: doc_id,
   section_id: section_id
  },
  token: @token
}
attachment_data =  JSON.parse(RestClient.post(url,params))

#4. add an attachment element to the section
elements_url =  "#{base}/elements.json?token=#{@token}"
params = {}

params["item"] = {
  element_type: 'attachments',
  container_type: 'ExperimentProcedure',
  container_id: section_id,
  data: [attachment_data].to_json
}
response = JSON.parse(RestClient.post(elements_url,params))

#5 update the attachment to associate with the element
element_id = response["id"]
attachment_data["element_id"] = element_id
attachment_id = attachment_data["id"]
url = "#{base}/attachments/#{attachment_id}.json?token=#{@token}"
params = {}
params["item"] = attachment_data
attachment_data =  JSON.parse(RestClient.put(url,params))
