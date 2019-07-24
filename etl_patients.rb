#get the patients
require 'uri'
require 'net/http'
require 'openssl'
require 'json'
require 'csv'
def get_remote_data(endpoint,exclude_fields='sequences,tags,member')
  token = ENV['token']
  puts "getting remote data from "
  url = URI("https://my.labguru.com/api/v1/#{endpoint}.json?token=#{token}&exclude_fields=#{exclude_fields}&meta=true&page_size=10")
  puts url
  http = Net::HTTP.new(url.host, url.port)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_NONE
  request = Net::HTTP::Get.new(url)
  response = http.request(request)
  puts response
  json = JSON.parse(response.read_body)
  data = [json["data"]]
  if json["meta"]["item_count"] > 20
    (2..json["meta"]['page_count']).each do |page|
      puts "#{url}&page=#{page}"
      request = Net::HTTP::Get.new("#{url}&page=#{page}")
      response = http.request(request)
      puts response
      json = JSON.parse(response.read_body)
      data << json["data"]
    end
  end
  data
end

def save_local_file(endpoint, data)
  if data && data.length > 0
    f = File.new(file_name(endpoint),"w")
    f.puts(data.to_json)
    f.close
  else
    raise "No Datax"
  end
end

def read_local_file(endpoint)
  JSON.parse(File.read(file_name(endpoint)), :symbolize_names => true)
end

def file_name(endpoint)
  fname = endpoint.split("/").last
  "#{fname}.json"
end
def get_data(endpoint)
  if File.exists?(file_name(endpoint))
    data = read_local_file(endpoint)
  else
    data = get_remote_data(endpoint).flatten
    save_local_file(endpoint,data)
  end
  data.flatten
end

def get_stocks
  get_remote_data('stocks.json')
end

def merge(patients,samples, rna_samples,protein_samples)
  data = []
  patients_by_uuid = {}
  patients.each do |p|
    patients_by_uuid[p[:uuid]] = p
  end
  rna_by_sample_uuid = {}
  rna_samples.each do |sample|
    rna_by_sample_uuid[sample[:links][0]] = sample
  end

  protein_by_sample_uuid = {}
  protein_samples.each do |sample|
    protein_by_sample_uuid[sample[:links][0]] = sample
  end

  patients_data = []
  samples.each do |sample|
    sample[:links].each do |link|
      if patients_by_uuid.keys.include?(link)
        patient = patients_by_uuid[link]
        data = [patient[:id], patient[:name], patient[:auto_name], patient[:Sex],patient[:Age],patient[:Diagnosis],patient[:Stage],patient[:TNM],patient[:'Diabetes Status']]
        data << sample[:'Sample Type']
        data << sample[:"Collection Tube"]
        data << sample[:Timepoint]
        data << sample[:"Date Sampled"]
        data << sample[:Isolated?]
        if (rna = rna_by_sample_uuid[sample[:uuid]])
          data << rna[:id]
          data << rna[:name]
        end
        if (protein = protein_by_sample_uuid[sample[:uuid]])
          data << protein[:id]
          data << protein[:name]
        end
        patients_data << data
      end
    end
  end
  patients_data
end
#extract
patients = get_data('biocollections/patients')
puts patients.length
samples = get_data('biocollections/patient%20samples')
puts samples.length
rna_samples = get_data('biocollections/rna%20samples')
puts rna_samples.length
protein_samples = get_data('biocollections/protein%20samples')
puts protein_samples.length

#transform
data =  merge(patients,samples,rna_samples,protein_samples)
CSV.open('merged.csv', "wb") do |csv|
  csv << ['Patient Id', 'Name', 'Auto Name', 'Sex', 'Age', 'Diagnosis', 'Stage', 'TNM','Diabetes Status', 'Sample Type', 'Collection Tube', 'Timepoint', 'Date Sampled', 'Isolated','RNA_ID','RNA_NAME','PROTEIN_ID','PROTEIN_NAME']
  data.each do |row|
    csv << row
  end
end

#load - to dataset


#get the patient samples
