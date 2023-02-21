import json
import requests
import logging
from dotenv import load_dotenv
import os
load_dotenv()

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

headers = {
"accept": "application/json",
"Content-Type": "application/x-www-form-urlencoded"
}

params = {
  "UserName": os.getenv('user'),
  "Password": os.getenv('pass'),
  "Tenant": os.getenv('tenant'),
  "GrantType": os.getenv('grantType')
}

r = requests.post("https://api.bmsemea.kaseya.com/v2/security/authenticate", data=params, headers=headers)
resp_dict = r.json()
token = resp_dict['result']['accessToken']


get_headers = {
  "Content-Type":"application/json",
  "Authorization": "Bearer " + token
}

g = requests.get("https://api.bmsemea.kaseya.com/v2/servicedesk/tickets/13287073/slainfo", headers=get_headers)
get_dict = g.json()
sla_info = get_dict['result']

data = []

post_headers = {
  "accept": "application/json",
  "Content-Type": "application/json"
}


for i in sla_info:
    dictionary = [{'respondGoal': 0['respondGoal']}]
    requests.post(os.getenv('powerBi_API'), json=dictionary, headers=post_headers)
