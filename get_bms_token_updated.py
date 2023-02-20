import json
import requests
import logging

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
  "UserName": "user",
  "Password": "pass",
  "Tenant": "company",
  "GrantType": "password"
}

r = requests.post("https://api.bmsemea.kaseya.com/v2/security/authenticate",  data=params, headers=headers)
resp_dict = r.json()
token = resp_dict['result']['accessToken']

sort_params = {
  "orderby": "id",
  "top": "15"
}

get_headers = {
  "Content-Type":"application/json",
  "Authorization": "Bearer " + token
}

g = requests.get("https://api.bmsemea.kaseya.com/v2/servicedesk/tickets", params=sort_params, headers=get_headers)
get_dict = g.json()
account_names = get_dict['result']

data = []

post_headers = {
  "accept": "application/json",
  "Content-Type": "application/json"
}

for i in account_names:
    dictionary = {'accountName': i['accountName'], 'dueDate': i['dueDate'], 'lastActivityUpdate': i['lastActivityUpdate'], 'openDate': i['openDate'], 
    'queueName': i['queueName'], 'ticketNumber': i['ticketNumber'], 'id': i['id'], 'title': i['title'], 'priorityName': i['priorityName'], 
    'statusName': i['statusName'], 'slaName': i['slaName'], 'assigneeName': i['assigneeName'], 'hasMetSLA': i['hasMetSLA'], 'slaStatusEnum': i['slaStatusEnum'], 
    'slaStatusEventId': i['slaStatusEventId']}

    try:
        requests.post("powerbiurl", json=dictionary, headers=post_headers)
    except Exception as e:
        print(e)
        continue

    ticket_num = i['id']
    str(ticket_num)
    # sort_params = {
    # "id": ticket_num
    # }
    g = requests.get('https://api.bmsemea.kaseya.com/v2/servicedesk/tickets/' + ticket_num + '/slainfo', params=sort_params, headers=get_headers)
    get_dict = g.json()
    sla_info = get_dict['result']

    if sla_info:
        dictionary2 = {'respondGoal': sla_info['respondGoal'], 'respondActual': sla_info['respondActual'], 'respondRemaining': sla_info['respondRemaining'], 'resolveGoal': sla_info['resolveGoal'], 
        'resolveActual': sla_info['resolveActual'], 'resolveRemaining': sla_info['resolveRemaining'], 'waitingActual': sla_info['waitingActual'], 'reopenActual': sla_info['reopenActual'], 
        'timeTotalGoal': sla_info['timeTotalGoal'], 'timeTotalActual': sla_info['timeTotalActual'], 'timeTotalRemaining': sla_info['timeTotalRemaining']}

        data.append(dict(dictionary, **dictionary2))

for item in data:
    try:
        requests.post("powerbiurl", json=item, headers=post_headers)
    except Exception as e:
        print(e)
        continue