import requests
import urllib.parse
import hashlib
import json as jsonlib

#HOST = 'https://backup.is-by.us'
API_VERSION = '/common_api/1.0/'
#PORT = 8089
#API_KEY = '4aaoI4Pp8m98XBjT55BYL57lj09XF9fa1b5E0SaA'

def request(address, port, api_key, command, params, post=False, json=False):
    try:
        if json:
            paramsFunc = jsonParams
        else:
            paramsFunc = urlencodeParams
        headers = getHeaders(api_key, params, paramsFunc, json)
        URL = address + ':' + str(port) + API_VERSION + command
        if post:
            req = requests.post(URL, verify=False, headers=headers,
            data=paramsFunc(params))
        else:
            req = requests.get(URL, params=params, verify=False, headers=headers)
        return req.json()
    except:
        return {'code': -1, 'descr': 'application error', 'data': {}}
    
def getHeaders(api_key, params, paramsFunc, json):
    headers = {}
    if json:
        headers['Content-Type'] = r'application/json'
    else:
        headers['Content-Type'] = r'application/x-www-form-urlencoded'
    headers['Signature'] = getSignature(api_key, params, paramsFunc)
    return headers
    
def getSignature(api_key, params, paramsFunc):
    md5 = hashlib.md5()
    md5.update((paramsFunc(params) + api_key).encode())
    return md5.hexdigest()
    
def urlencodeParams(params):
    return urllib.parse.urlencode(params)
    
def jsonParams(params):
    return jsonlib.dumps(params)
