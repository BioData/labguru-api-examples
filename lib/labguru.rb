require 'faraday'
require 'json'

class Labguru
 API_URL = "https://my.labguru.com" 
 def initialize(email,password)
   @base = "https://api.labguru.com"
   @email = email 
   @password = password
   @token = login(@email, @password)
 end

 def token 
 	return @token
 end
 #returns a token or -1 for null vallues. 
 def login(email = "",password = "")
   endpoint = "/api/v1/sessions.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {login: email, password: password})
   json = JSON.parse(response.body)
   return json["token"]
 end 

 def add_project(name, description = "")
   endpoint = "/api/v1/projects.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {item:{title: name, description: description}, token:@token})
   return_id(response.body, "Projects::Project")
 end 

 def add_folder(project_id,name,description = "")
   endpoint = "/api/v1/milestones.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {item:{project_id: project_id, title: name, description: description}, token:@token})
   return_id(response.body,"Projects::Milestone")
 end 
 
 def add_experiment(project_id,folder_id,name)
   endpoint = "/api/v1/experiments.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {item:{project_id: project_id, milestone_id: folder_id, title: name}, token:@token})
   return_id(response.body, "Projects::Experiment")
 end

 def add_section(experiment_id,name,position = 999)
  endpoint = "/api/v1/element_containers.json"
  response = Faraday.post("#{API_URL}#{endpoint}", {item:{container_type: "Projects::Experiment" ,container_id: experiment_id, name: name,position: position}, token:@token})
  return_id(response.body,"ExperimentProcedure")
 end 

 def add_element(section_id, type = "text" , data)
   endpoint = "/api/v1/elements.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {item:{container_type: "ExperimentProcedure" ,container_id: section_id, element_type: type, data: data}, token:@token})
   return_id(response.body,"Element")
 end

 def add_paper(pmid)
   url = "https://my.labguru.com/knowledge/papers/p#{pmid}.json?token=#{@token}"
   response = Faraday.get(url)
   return_id(response.body,"Knowledgebase::Paper")
 end 

 def add_attachment(object_id,object_type, file_name )

 end

 def add_link(source_id, source_class, target_id, target_class)
   endpoint = "/api/v1/links.json"
   response = Faraday.post("#{API_URL}#{endpoint}", {item:{source_type: source_class, source_id: source_id, target_type: target_class, target_id: target_id}, token:@token})
   return_id(response.body, "Link")
 end
 
 def return_id(body,object_type)
   json = JSON.parse(body)
   {id: json["id"], uuid: json["uuid"] || "???" , object_type: object_type} 
 end

 def new_element(type)
   case type
   when :steps 
   	Steps.new
   end
 end
 
 class Steps
  def initialize 
    @steps = []
  end

  def add_step(body,timer = {hour: 0, minutes: 0, seconds: 0},completed = false)
   @steps << {title: body, timer:timer , completed: completed}
  end

  def to_json 
    JSON.pretty_generate(chair)
  end 
 end
end
