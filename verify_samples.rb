require 'csv'
require 'rest-client'
require 'json'
EMAIL = "jonathan.gross@biodata.com"
PASSWORD = "Jwk7PQtzJy"
#if you are using a private cloud / local install you will need to use a different url.
@base = "https://my.labguru.com"


def find_stock_by_barcode(barcode)
  url = @base + "/api/v1/stocks.json"
  url = "#{url}?token=#{@token}&filter={\"barcode\":\"#{barcode}\"}"
  JSON.parse(RestClient.get(url))
end

def get_experiment_sample_list(exp_id)
  url = @base + "/api/v1/experiments/#{exp_id}/elements.json"
  url = "#{url}?token=#{@token}&by_type=samples"
  puts url
  JSON.parse(RestClient.get(url))
end

def ensure_stock_is_in_sample_list(json,stock_id)
  data = json
  ids = []
  stocks = JSON.parse(data[0]["data"])["samples"][0]["stocks"]
  stocks.each do |stock|
    (ids << stock["id"]) if stock && stock.keys && stock.keys.include?("id")
  end
  found = ids.include? (stock_id)
  puts found
  found
end


#1. Get a token
url = @base + "/api/v1/sessions.json"
params = {login: EMAIL,password: PASSWORD}
response = JSON.parse(RestClient.post(url,params))
@token = response["token"]

#2.we get the experiment id from the console, we could also got it from the csv
# run this script
# ruby verify_samples.rb 50945
experiment_id = ARGV[0]
puts experiment_id
sample_list = get_experiment_sample_list(experiment_id)

#3. create an verification file to write to.
verification_path = "verification_#{experiment_id}.txt"
verification  = File.new(verification_path,"w")

#4. read samples file
CSV.foreach("samples.csv") do |sample|
  stock = find_stock_by_barcode(sample[0])[0]
  if stock
    found = ensure_stock_is_in_sample_list(sample_list,stock["id"])
    verification.puts("#{sample},#{found ? :'Veified': 'NOT-VERIFIED'}")
  else
    verification.puts("#{sample},'NOT FOUND'")
  end
end

#5. upload the file
verification.close

url = @base + "/api/v1/attachments.json"
params = {
  item: {
   title: "Experiment Verification File",
   attachment: File.open("verification_#{experiment_id}.txt","r"),
   attachable_type: "Projects::Experiment",
   attachable_id: experiment_id
  },
  token: @token
}
response =  JSON.parse(RestClient.post(url,params))
