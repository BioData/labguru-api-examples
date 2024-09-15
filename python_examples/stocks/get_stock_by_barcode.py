import requests
from getpass import getpass
import json

LABGURU_HOST = "http://localhost:3000/api/v1/"

barcode = 112654
token = "TOKENGOESHERE"

url = f"{LABGURU_HOST}/stocks/get_stocks_by_barcode?input={barcode}&token={token}"
stocks = requests.get(url)
stock = stocks.json()[0]
