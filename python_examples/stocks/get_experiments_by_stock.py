import requests
from getpass import getpass
import json

LABGURU_HOST = "http://localhost:3000/api/v1/"

barcode = 112654
token = "TOKENGOESHERE"


url = f"{LABGURU_HOST}/stocks/get_stocks_by_barcode?input={barcode}&token={token}"
stocks = requests.get(url)
stock = stocks.json()[0]


url = f"{LABGURU_HOST}/experiments/item_experiments?item_id={stock['id']}&item_class=System::Storage::Stock&token={token}"
experiments = requests.get(url)

print(f"There are {len(experiments.json())} experiments associated to {barcode}")
print("The experiments' locations in the system:")
for exp in experiments.json():
    print(f"Experiment #{exp['id']} - {exp['name']}")
    print(f"  Is part of project #{exp['project']['id']} - {exp['project']['name']}")
    print(f"  At folder #{exp['milestone']['id']} - {exp['milestone']['name']}")
    print(
        "============================================================================="
    )
