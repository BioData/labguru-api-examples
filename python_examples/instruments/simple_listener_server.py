from flask import Flask, request, jsonify
import re
import os
import requests

app = Flask(__name__)

# List of instrument IDs you are syncing
synced_instrument_ids = [12]
labguru_token = os.environ.get('LABGURU_TOKEN')
base = "http://localhost:3000" # Replace with your Labguru server base URL

def register_labguru_webhook():
   url = f"#{base}/api/v1/webhooks"
   querystring = {"token": labguru_token}
   payload = {
    "token": labguru_token,
    "item": {
        "trigger_key": "system_event.create",
        "active": 1,
        "url": "http://localhost:3001/labguru-webhook"
      }
    }
   headers = {"Content-Type": "application/json"}
   response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
   if response.status_code == 201:
     print("Webhook registered successfully.")
   else:
     print(f"Failed to register webhook: {response.status_code} {response.text}")


@app.route('/labguru-webhook', methods=['POST'])
def handle_labguru_webhook():
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")

    payload = request.get_json()
    if isinstance(payload, list):
        payload = payload[0]

    input_type = payload.get('input_type')
    input_id = payload.get('input_id')
    input_txt = payload.get('input_txt', '')
    url = payload.get('url')
    changes = payload.get('changes', {})

    # Extract event_type from input_txt
    match = re.search(r'activity_key: (\w+\.\w+)', input_txt)
    if match:
        event_type = match.group(1)
    else:
        event_type = None
    
    print(f"Received event_type: {event_type}, input_type: {input_type}, input_id: {input_id}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    register_labguru_webhook()
    app.run(host='0.0.0.0', port=3001, debug=True)
