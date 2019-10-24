# Add an image to an equipment using the API

require 'rest-client'
require 'json'

#Steps:
#1. Get a token
#2. Find the Equipment you want to add files to
#3. Upload and attach an image to this equipment

#1. Get a token
development: @base = 'http://localhost:3000'
sgs: @base = "https://sgs.labguru.com"
url = @base + "/api/v1/sessions.json"
params = {login: EMAIL, password: PASSWORD}
response = JSON.parse(RestClient.post(url, params))
@token = response["token"]

#2. Find the equipment you want to add files to
def search_equipment_by_name(name)
  url = @base + "/api/v1/instruments.json?token=#{@token}&name=#{name}"
  puts url
  response = JSON.parse(RestClient.get(url))
end

# make sure you found the right equipment
equipment = search_equipment_by_name("McHammer")
if equipment.count == 1 # only one found
  equipment = equipment.first
  puts equipment
elsif equipment.count == 0 # non found
  puts "No equipment found"
else # need to sharpen the search term to find only one
  puts "choose one of these assets"
  puts equipment
end

#3. Upload and attach an image to this equipment
def upload_attachment_to_equipment(equipment, attachment_args)
  url = @base + "/api/v1/attachments.json"
  params = {
    item: {
     title: attachment_args[:title],
     description: attachment_args[:description] || "Some description of this image, not mandatory",
     attachment: File.open(attachment_args[:path],"r"),
     attach_to_uuid: equipment["uuid"]
    },
    token: @token
  }
  response =  JSON.parse(RestClient.post(url,params))
end
upload_attachment_to_equipment(equipment, {path: "/Users/liron/My\ Documents/sgs/mchammer.png", title: "mchammer"})
# if needed to go through a whole folder do this:
# go through all files in a folder:
folder_path = "/Users/liron/My\ Documents/sgs/"
attachment_args = {path: "#{folder_path}/mchammer.png", title: "mchammer"}
upload_attachment_to_equipment(equipment, attachment_args)

