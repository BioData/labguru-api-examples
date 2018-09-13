require 'rest-client'
require 'json'

#Steps:
#1. Get a token
#2. Find the experiment you want to add results to 
#3. Find the results section 
#4. Add an text element to the results section 
#5. Upload and attach an image to this experiment
#6. Embed the image inside the result element 
#7. Save the element

#1. Get a token 
@base = "https://api.labguru.com"
url = @base + "/api/v1/sessions.json"
params = {login: "EMAIL",password: "PASSWORD"}
response = JSON.parse(RestClient.post(url,params))
@token = response["token"]

#2. Find the experiment you want to add results to 
#2.1 Get a list of experiments 
#2.2 Find the experiment needed
def fetch_experiments(page)
  puts page
  url = @base + "/api/v1/experiments.json?token=#{@token}&page=#{page}"
  response = JSON.parse(RestClient.get(url))
end 

def find_experiment_by_title(name)
  page = 1 
  experiment = nil
  loop do 
    experiments = fetch_experiments(page) 
    titles = experiments.map(){|experiment| experiment["title"]}
    if titles.include?(name)
      experiment = experiments[titles.find_index(name)]
    end
    page = page + 1
    break if experiments.empty? || !experiment.nil?
  end
  experiment 
end

# change to your experiment title 
experiment = find_experiment_by_title("EXPERIMENT_NAME")

#3. Find the results section 
procedures = experiment["experiment_procedures"]

def get_section(experiment,section_to_find)
   section = experiment["experiment_procedures"].find(){|ep| ep["experiment_procedure"]["section_type"] == section_to_find}
   section["experiment_procedure"] if section
end
results = get_section(experiment,"results")

#4. Add an text element to the results section 
def add_element_to_section(section,type,data)
  url = @base + "/api/v1/elements.json"
  params =  {"item"=>{"element_type"=> type, "data"=>data, "container_type"=>"ExperimentProcedure", "container_id"=>section["id"], "field_name"=>section["section_type"]},token: @token}
  response = JSON.parse(RestClient.post(url,params))
end
element = add_element_to_section(results,"text","result text goes here")

#5. Upload and attach an image to this experiment
url = @base + "/api/v1/attachments.json"
params = {
  item: {
   title: "IMG_0365",
   description: "Our experiment result",
   attachment: File.open("/Users/admin/Desktop/IMG_0365.jpg","r"),
   attach_to_uuid: experiment["uuid"]
  },
  token: @token
}
response =  JSON.parse(RestClient.post(url,params))

image_url = response["annotated_url"].split("?").first

#6. Add image to results 
element["data"] << "<img src='#{image_url}'/>"
#7. Save element
def save_element(element)
  url = @base + "/api/v1/elements/#{element["id"]}.json"
  response = JSON.parse(RestClient.put(url,{token: @token, item: element}))
end

save_element(element)
