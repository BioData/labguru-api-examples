require 'rest-client'
require 'json'
@base = "https://us.labguru.com/api/v1/"


#1. Get a token
url = @base + "sessions.json"
params = {login: "EMAIL",password: "PASSWORD"}
response = JSON.parse(RestClient.post(url,params))
token = response["token"]

#2. In the current directory list of the Genebank files
files = Dir["*.gb"]

#3. Upload each file, instruct labguru to create a plasmid from the uploaded file

def upload_file(file,token)
  url = @base + "attachments.json"
  params = {
    item: {
     title: "Genbank File #{file}",
     description: "Uploaded Via API as part of a batch upload on #{Date.today}",
     attachment: File.open(file,"r")
    },
    token: @token
  }
  response =  JSON.parse(RestClient.post(url,params))
end

def build_plasmids_from_gb(attachment_id,token)
  url = @base + "plasmids.json"
  params = {
    item: {
     :gb_attachment_id => attachment_id
    },
    token: @token
  }
  response =  JSON.parse(RestClient.post(url,params))
end


files.each do |file|
  attachment_id = uploaded_file(file,token)["id"]
  build_plasmids_from_gb(attachment_id,token)
end
