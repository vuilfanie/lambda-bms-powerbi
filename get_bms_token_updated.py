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

r = requests.post("https://api.bmsemea.kaseya.com/v2/security/authenticate",  data=params, headers=headers)
resp_dict = r.json()
token = resp_dict['result']['accessToken']

sort_params = {
  "order_by": "id",
  "top": "3",
  "sort_by": "desc"
}

get_headers = {
  "Content-Type":"application/json",
  "Authorization": "Bearer " + token
}

g = requests.get("https://api.bmsemea.kaseya.com/v2/servicedesk/tickets", params=sort_params, headers=get_headers)
get_dict = g.json()

account_names = get_dict['result']

ticket_ids = []
for x in account_names:
    ticket_ids.append(x['id'])

num = os.getenv('top_tickets')

print(num)

ticket_id_top = ticket_ids[:int(num)]

tickets = []
for z in ticket_id_top:
    match = next(d for d in account_names if d['id'] == z)
    tickets.append(match)


post_headers = {
  "accept": "application/json",
  "Content-Type": "application/json"
}

for i in tickets:
    data = []
    dictionary = {'accountName': i['accountName'], 'dueDate': i['dueDate'], 'lastActivityUpdate': i['lastActivityUpdate'], 'openDate': i['openDate'], 
    'queueName': i['queueName'], 'ticketNumber': i['ticketNumber'], 'id': i['id'], 'title': i['title'], 'priorityName': i['priorityName'], 
    'statusName': i['statusName'], 'slaName': i['slaName'], 'assigneeName': i['assigneeName'], 'hasMetSLA': i['hasMetSLA'], 'slaStatusEnum': i['slaStatusEnum'], 
    'slaStatusEventId': i['slaStatusEventId']}

    ticket_num = i['id']
    sort_params = {
    "id": ticket_num
    }
    s = requests.get('https://api.bmsemea.kaseya.com/v2/servicedesk/tickets/' + str(ticket_num) + '/slainfo', params=sort_params, headers=get_headers)
    get_dict = s.json()
    sla_info = get_dict['result']

    dictionary2 = {'respondGoal': sla_info['respondGoal'], 'respondActual': sla_info['respondActual'], 'respondRemaining': sla_info['respondRemaining'], 'resolveGoal': sla_info['resolveGoal'], 
    'resolveActual': sla_info['resolveActual'], 'resolveRemaining': sla_info['resolveRemaining'], 'waitingActual': sla_info['waitingActual'], 'reopenActual': sla_info['reopenActual'], 
    'timeTotalGoal': sla_info['timeTotalGoal'], 'timeTotalActual': sla_info['timeTotalActual'], 'timeTotalRemaining': sla_info['timeTotalRemaining'], 'ticketPriorityColor': sla_info['ticketPriorityColor']}
    dictionary.update(dictionary2)
    data.append(dictionary)
    requests.post(os.getenv('powerBi_API'), json=data, headers=post_headers)
