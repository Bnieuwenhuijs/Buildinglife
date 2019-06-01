import json
import requests

url = 'https://bag.basisregistraties.overheid.nl/api/v1/panden/{0193100000033336}'
headers = {'X-Api-Key': '8d2869b4-2b78-4596-b290-6f2e1e8b4661'}

r = requests.get(url, headers=headers)
b = r.json()
print(b)