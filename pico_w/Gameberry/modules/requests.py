import urequests
import gc

def GET(url):
    gc.collect()
    response = urequests.get(url)
    return response

def POST(url, data):
    gc.collect()
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, data=data, headers=headers)
    return response
