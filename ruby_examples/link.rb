#https://github.com/rest-client/rest-client
require 'rest-client'
require 'json'
require 'csv'

def base
  "https://my.labguru.com/api/v1"
end

def get_token(username,password)
  url = base + "/sessions.json"
  params = {login: username,password: password}
  response = JSON.parse(RestClient.post(url,params))
  token = response["token"]
end

def extract_uuid(response)
  JSON.parse(response)[0]["uuid"]
end

#returns a UUID of the entity requrested
def find_item(model,name)
  name = name.strip
  model = model.strip
  ret = nil
  url = "#{base}/#{model}"
  query = URI.escape "#{url}?token=#{@token}&name=#{name}"
  write_log(query)
  response = RestClient.get(query)
  ret = extract_uuid(response) if response
  return ret
end

def create_link(source_uuid, target_uuid)
  write_log("creating links between #{source_uuid} and #{target_uuid}")
  url  = "#{base}/links.json"
  params = {}
  params['token'] = @token
  params['item']= {}
  params['item']['source_uuid'] = source_uuid
  params['item']['target_uuid'] = target_uuid
  RestClient.post(url,params)
end


def parse_line(line)
  links_made = 0
  pairs = line.each_slice(2).to_a
  source_type, source_name = *pairs.shift #get the first pair in the line.
  write_log("searching for source #{source_type} with #{source_name}")
  source = find_item(source_type, source_name)
  pairs.each do |target|
    write_log "searhing for target #{target[0]} with name #{target[1]}"
    target = find_item(*target)
    if target
      if create_link(source,target)
        links_made += 1
      end
    end
  end
  links_made
end

def write_log(msg)
  puts msg
  @log.puts(msg)
end

def read_and_parse_file(file)
  unless File.exists?(file)
    write_log "File not found"
    return
  end
  csv = CSV.readlines(file)
  csv.each_with_index do |line,i|
    begin
      ret = parse_line(line )
      write_log "#{i}: links created: #{ret} "
    rescue StandardError => err
      write_log "Error in Line #{i} - #{err}"
    end
  end
end

if ARGV[0] == '--help'
  puts "ruby link.rb email password csv_filename"
  puts "the structure of the csv:"
  puts "type, name, type, name, type, name"
  puts "for example:"
  puts "protocols, gfp screen, materials, gfp, antibodies, anti-gfp"
  puts "line above will create two links'"
  puts '"gfp screen" protocol will be linked to the "gfp" material'
  puts '"gfp screen" protocol will be linked to the "anti-gfp" antibody'
  puts 'if you are linking to a custom collection - your type should look like:'
  puts 'generics/{collection name},name'
else
  #create a log file for the links created -
  #send us this file if things do not work as expected
  @log = File.new("links_#{Time.now.to_i}.log","w")
  @token = get_token( ARGV[0],ARGV[1])
  if @token == "-1"
    write_log "could not autenticate user"
  else
    read_and_parse_file(ARGV[2])
  end
  @log.close
end
