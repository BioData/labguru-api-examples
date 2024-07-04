require 'rest-client'
require 'json'
@base = "https://jonathan.labguru.com"
@api_base = "#{@base}/api/v1/"
#1. Get a token
url = @api_base + "sessions.json"
params = {login: "jonathan.gross+201703@biodata.com",password: "123456"}
response = JSON.parse(RestClient.post(url,params))
@token = response["token"]
#2. In the current directory list of the Genebank files
files = Dir["*.gb"]

#3. Upload each file, instruct labguru to create a plasmid from the uploaded file

def upload_file(file,token)
  url = @api_base + "attachments.json"
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

def build_plasmids_from_gb(file, attachment_id,token)
  url = @api_base + "plasmids.json"
  params = {
    item: {
     gb_attachment_id: attachment_id
    },
    token: @token
  }
  response =  JSON.parse(RestClient.post(url,params))
end


files.each do |file|
  attachment_id = upload_file(file,@token)["id"]
  response = build_plasmids_from_gb(file, attachment_id,@token)
  puts "uploded - #{file} to - #{@base}#{response["url"]}"
end
