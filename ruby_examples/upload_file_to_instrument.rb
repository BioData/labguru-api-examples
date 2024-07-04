require 'rest-client'
require 'json'
def usage
 puts "ruby upload_file_to_instrument {instrument_id} {filename}"
end
if ARGV[0].nil? || ARGV[1].nil?
  usage
  exit
end

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

#2. get the instrument based on the input id
url = @base +  "instruments/#{ARGV[0]}.json" + "?token=#{@token}"
puts url.gsub(@token, "TOKEN")
begin
  response = RestClient.get(url)
rescue RestClient::NotFound
  puts "Error fetching instrument"
  exit 1
end

@instrument =  JSON.parse(response)

#upload file
url = @base + "/attachments.json"
params = {
  item: {
   title: "#{ARGV[1]}",
   description: "Our experiment result",
   attachment: File.open(ARGV[1],"r"),
   attach_to_uuid: @instrument["uuid"]
  },
  token: @token
}
attachment =  JSON.parse(RestClient.post(url,params))
puts attachment
