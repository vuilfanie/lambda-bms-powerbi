import requests
import json
import os

BMS_API_USERNAME = "apiuser"
BMS_API_PASSWORD = "BStr@nd67."
BMS_API_SERVER = os.environ.get('BMS_API_SERVER') or 'https://api.bmsemea.kaseya.com'
BMS_API_TENANT = "gravit8 it"
BMS_API_TOP = os.environ.get('BMS_API_TOP') or "15"
POWERBI_API = "https://api.powerbi.com/beta/3e84c1e6-c1ae-498b-84b5-b33c7f182800/datasets/45bb1868-0902-45d4-b29e-c4c5f1f9ba55/rows?key=OeiDv2gSt%2BgZUPkkkzogwluAX0L7Kq1EgnqzX6Z0rFedauTP0zvbkvTDposF64nWsDiAVLgf0FwvoLtuYa%2FO2Q%3D%3D"

access_token = ''

def web_call(method, url, payload):
    opt = {
        'method': method,
        'headers': {
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
            'Authorization': 'Bearer ' + access_token
        },
        'json': True
    }

    if url.startswith('https') is False:
        opt['uri'] = BMS_API_SERVER + url
    else:
        opt['uri'] = url

    if url.startswith('/v2/security/authenticate'):
        opt['form'] = payload
    else:
        opt['body'] = payload

    if access_token == '': 
        del opt['headers']['Content-Type']
        del opt['headers']['Authorization']

    print(f'web_call(): calling {opt["uri"]}')

    try:
        res = requests.request(**opt)
        return res
    except Exception as err:
        print('web_call(): FAIL: ', err)
        return False

def login():
    login_promise = web_call(
        'POST',
        '/v2/security/authenticate',
        {
            'UserName': BMS_API_USERNAME,
            'Password': BMS_API_PASSWORD,
            'GrantType': "password",
            'Tenant': BMS_API_TENANT
        }
    )

    try:
        access_token = login_promise.json()['accessToken']
        print('login(): access token received -> ', access_token)
        return access_token
    except Exception as err:
        print('login(): FAIL: ', err)
        return False

def get_tickets():
    get_ticket_promise = web_call(
        'GET',
        '/v2/servicedesk/tickets?$orderby=id desc&$top=' + BMS_API_TOP,
        {}
    )

    try:
        ticket_payload = get_ticket_promise.json()
        print('get_tickets(): received payload, no. of results: ', ticket_payload['TotalRecords'])

        reduced_payload = [
            {
                'accountName': ticket['accountName'],
                'dueDate': ticket['dueDate'],
                'lastActivityUpdate': ticket['lastActivityUpdate'],
                'openDate': ticket['openDate'],
                'queueName': ticket['queueName'],
                'statusName': ticket['statusName'],
                'ticketNumber': ticket['ticketNumber'],
                'title': ticket['title']
            } for ticket in ticket_payload['Result']
        ]

        opt = {
            'method': 'POST',
            'uri': POWERBI_API,
            'json': reduced_payload
        }

        res = requests.request(**opt)
        if res.status_code == 200:
            print('get_tickets(): sendToPowerBI(): Success')
            return True
        else:
            print('get_tickets(): sendToPowerBI(): FAIL: ', res.text)
            return False
    except Exception as err:
            print('get_tickets(): sendToPowerBI(): FAIL: ', err)
            return False

def get_bms_tickets():
    print('get_bms_tickets: triggered')

    access_token = login()
    if access_token is False:
        return False

    success = get_tickets()
    if success is True:
        print('ticket work done')
        return {'statusCode': 200, 'body': json.dumps({ 'message': 'job complete'})}
    else:
        return False

if __name__ == "__main__":
    get_bms_tickets()