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

def download_file(url, filename):
    response = GET(url)
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
            response.close()
            return True
    else:
        response.close()
        return False