import requests
import os
import json

# Get the token and server base from the user or environment variables
token = input("Enter token: ") or os.environ.get("LABGURU_TOKEN")
server_base = (
    input("Enter server base (e.g., https://my.labguru.com/): ")
    or "http://localhost:3000"
)

# Get the URLs to add to the section
urls = input("Enter the URLs (comma-separated): ").split(",")

# Define the LabGuru experiment ID (Replace these with actual values)
experiment_id = input("Enter the experiment ID: ")

# API URL for creating a new section
create_section_url = f"{server_base}/api/v1/sections?token={token}"

# Prepare the payload to create the "Remote Files" section
section_data = {
    "item": {
        "name": "Remote Files",
        "experiment_id": experiment_id,
        "container_type": "Projects::Experiment",
        "container_id": experiment_id,
    }
}

# Set the headers for the request
headers = {"Content-Type": "application/json"}

# First request: Create the "Remote Files" section
response = requests.post(
    create_section_url, headers=headers, data=json.dumps(section_data)
)

# Check if the section was created successfully
if response.status_code == 201:
    section = response.json()
    section_id = section["id"]
    print("Section created successfully. Section ID:", section_id)
else:
    print("Failed to create section.")
    print("Response:", response.json())
    exit()

# API URL for adding elements to the section
create_element_url = f"{server_base}/api/v1/elements?token={token}"

# Add URLs as text elements with href links in the "Remote Files" section
for url in urls:
    # Prepare the payload for the text element
    element_data = {
        "item": {
            "container_id": section_id,
            "container_type": "ExperimentProcedure",
            "element_type": "text",
            "readonly": True,
            "data": f'<a href="{url.strip()}" target="_blank">{url.strip()}</a>',
        }
    }

    # Second request: Add the URL element to the section
    response = requests.post(
        create_element_url, headers=headers, data=json.dumps(element_data)
    )

    # Output the status of the element creation
    if response.status_code == 201:
        print(f"Element for URL {url.strip()} added successfully.")
    else:
        print(f"Failed to add element for URL {url.strip()}.")
        print("Response:", response.json())
