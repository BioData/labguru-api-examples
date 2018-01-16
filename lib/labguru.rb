require 'faraday'
require 'json'

class Labguru
 API_URL = "https://my.labguru.com" 
 def initialize(email,password)
   @base = API_URL
   @email = email 
   @password = password
 end

 def login(email = @email, password = @password)
   @token = do_login(email, password)
 end

 def server=(base)
   @base = base
 end

 def token 
 	return @token
 end
 #returns a token or -1 for null vallues. 
 def do_login(email = "",password = "")
   endpoint = "/api/v1/sessions.json"
   response = Faraday.post("#{@base}#{endpoint}", {login: email, password: password})
   json = JSON.parse(response.body)
   return json["token"]
 end 

 def add_project(name, description = "")
   endpoint = "/api/v1/projects.json"
   response = Faraday.post("#{@base}#{endpoint}", {item:{title: name, description: description}, token:@token})
   return_id(response.body, "Projects::Project")
 end 

 def add_folder(project,name,description = "")
   endpoint = "/api/v1/milestones.json"
   response = Faraday.post("#{@base}#{endpoint}", {item:{project_id: project['id'], title: name, description: description}, token:@token})
   return_id(response.body,"Projects::Milestone")
 end 
 
 def add_experiment(project,folder,name)
   endpoint = "/api/v1/experiments.json"
   response = Faraday.post("#{@base}#{endpoint}", {item:{project_id: project['id'], milestone_id: folder['id'], title: name}, token:@token})
   return_id(response.body, "Projects::Experiment")
 end

 def add_section(container,name,position = 999)
  endpoint = "/api/v1/element_containers.json"
  response = Faraday.post("#{@base}#{endpoint}", {item:{container_type: "Projects::Experiment" ,container_id: container['id'], name: name,position: position}, token:@token})
  return_id(response.body,"ExperimentProcedure")
 end 

 def add_element(container, type = "text" , data)
   endpoint = "/api/v1/elements.json"
   response = Faraday.post("#{@base}#{endpoint}", {item:{container_type: "ExperimentProcedure" ,container_id: container['id'], element_type: type, data: data}, token:@token})
   return_id(response.body,"Element")
 end

 def add_paper(pmid)
   url = "#{@base}/knowledge/papers/p#{pmid}/add_pubmed.json?token=#{@token}"
   response = Faraday.get(url)
   return_id(response.body,"Knowledgebase::Paper")
 end 

 def add_attachment(object, file_path, name, description )
    endpoint = "/api/v1/attachments.json"
    response = Faraday.post("#{@base}#{endpoint}", {item:{ 
      title: name,
      description: description,
      attachment: File.open(path,"r"),
      attach_to_uuid: object['uuid']}, token:@token})
    return_id(response.body,"System::Attachment")
 end

 def add_link(source_id, source_class, target_id, target_class)
   endpoint = "/api/v1/links.json"
   response = Faraday.post("#{@base}#{endpoint}", {item:{source_type: source_class, source_id: source_id, target_type: target_class, target_id: target_id}, token:@token})
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
