require 'rest-client'
require 'json'
file = ARGV[0]
experiment_id = ARGV[1]

password = ENV["LABGURU_PASSWORD"]
email = ENV["LABGURU_EMAIL"]

#1. Get a token
@base = "https://my.labguru.com/api/v1/"
url = @base + "sessions.json"
params = {login: email ,password: password}
response = JSON.parse(RestClient.post(url,params))
@token = response["token"]
if @token == "-1"
  puts "Check Email / Password"
  return
end

#2. Convert the spreadJS to JSON element
url = "http://spreadjs.cloudapp.net/Myapp/Home/Import"
file_name = File.open(file, "r")
json = RestClient.post(url,{filename: file_name})
f = File.new(file.gsub('xlsx','json'),"w")
f.puts json
f.close
#3. Get Experiment by ID
def fetch_experiment(id)
  url = @base + "experiments/#{id}.json?token=#{@token}"
  puts url
  response = JSON.parse(RestClient.get(url))
end

experiment = fetch_experiment(experiment_id)
procedures = experiment["experiment_procedures"]

#4. Get the Results Section
def get_section(experiment,section_to_find)
   section = experiment["experiment_procedures"].find(){|ep| ep["experiment_procedure"]["section_type"] == section_to_find}
   section["experiment_procedure"] if section
end
results = get_section(experiment,"results")

#5. Add an excel element to the results section
def add_element_to_section(section,type,data)
  url = @base + "elements.json"
  params =  {"item"=>{"element_type"=> type, "data"=>data, "container_type"=>"ExperimentProcedure", "container_id"=>section["id"], "field_name"=>section["section_type"]},token: @token}
  response = JSON.parse(RestClient.post(url,params))
end
element = add_element_to_section(results,"excel",json)

#6. Get the PDF of the spreadJS
# url = "http://spreadjs.cloudapp.net/Myapp/Home/Export"
# pdf = RestClient.post(url,dataObj = {
#             "spread": json.to_json,
#             "exportFileType": "pdf",
#             "pdf": {
#                 "sheetIndexes": [0],
#                 "setting": {
#                   "author": "",
#                   "centerWindow": false,
#                   "creator": "",
#                   "displayDocTitle": false,
#                   "fitWindow": false,
#                   "hideMenubar": false,
#                   "hideToolbar": false,
#                   "hideWindowUI": true,
#                   "keywords": "",
#                   "subject": "",
#                   "title": ""}
#
#         }})
#
# f = File.new("test.pdf","w")
# f.puts(pdf)
# f.close
#7. Upload the files
