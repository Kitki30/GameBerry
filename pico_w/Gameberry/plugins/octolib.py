import modules.requests as requests
import ujson
import gc
import urequests

octoPrintUrl = ""
octoApiKey = ""

def setOctoPrintUrl(url):
    global octoPrintUrl 
    octoPrintUrl = url

def setOctoPrintApiKey(apiKey):
    global octoApiKey 
    octoApiKey = apiKey


def appKeysProbe():
    global octoPrintUrl
    request = requests.GET(octoPrintUrl + "/plugin/appkeys/probe")
    if request.status_code == 204:
        request.close()
        return True
    else:
        request.close()
        return False
    
def appKeysRequest(appName):
    global octoPrintUrl
    post_data = ujson.dumps({"app": appName})
    request = requests.POST(octoPrintUrl + "/plugin/appkeys/request", post_data)
    if request.status_code == 201:
        apptoken = request.json()["app_token"]
        request.close()
        accepted = False
        checks = 0
        token = ""
        print("Waiting for users choice")
        while accepted == False and checks < 60:
            gc.collect()
            rq = requests.GET(octoPrintUrl + "/plugin/appkeys/request/"+apptoken)
            if rq.status_code == 200:
                token = rq.json()["api_key"]
                accepted = True
            elif rq.status_code == 404:
                checks == 30
                print("Error 404")
                rq.close()
            checks = checks + 1
        return token
    
def getPrinterProfiles():
    rq = requestGet("/api/printerprofiles")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return json
    else:
        print("Status code other than 200")
        gc.collect()
        return ""
    
def getPrinterProfile(name):
    rq = requestGet("/api/printerprofiles")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        try:
            return json["profiles"][name]
        except:
            print("Cannot get print profile "+ name)
            return ""
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""

def testApiKey():
    rq = requestGet("/api/server")
    code = rq.status_code
    rq.close()
    if code == 200:
        return True
    else:
        return False

def getTemps():
    rq = requestGet("/api/printer?exclude=state,sd")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return json
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""
    
def getState():
    rq = requestGet("/api/printer?exclude=state,temperature")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return json
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""
    
def getConnetion():
    rq = requestGet("/api/connection")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return json
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""
    
def connect():
    post_data = ujson.dumps({"command": "connect"})
    rq = requestPost("/api/connection", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    else:
        rq.close()
        return False

def disconnect():
    post_data = ujson.dumps({"command": "disconnect"})
    rq = requestPost("/api/connection", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    else:
        rq.close()
        return False
    
def getSdCardState():
    rq = requestGet("/api/printer/sd")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return sdStateResponse(json["ready"])
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""
    
def apiVersion():
    rq = requestGet("/api/version")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return apiVersionResponse(json["api"],json["server"],json["text"])
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return None
    
def getSystemCommands():
    rq = requestGet("/api/system/commands")
    code = rq.status_code 
    json = rq.json()
    rq.close()
    if code == 200:
        gc.collect()
        return json
    else:
        print("Status code: "+str(code)+"\n"+str(json))
        gc.collect()
        return ""
    
def executeSystemCommand(source, action):
    post_data = ujson.dumps({"command": "connect"})
    rq = requestPost("/api/connection", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    elif rq.status_code == 404:
        print("command not found")
        rq.close()
        return False
    else:
        rq.close()
        return False
    
def setToolheadTemperature(temp, toolheadNumber = 0):
    post_data = ujson.dumps({"command": "target", "targets": {"tool"+str(toolheadNumber): temp}})
    rq = requestPost("/api/printer/tool", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    elif rq.status_code == 404:
        print("command not found")
        rq.close()
        return False
    else:
        rq.close()
        return False
    
def setBedTemperature(temp):
    post_data = ujson.dumps({"command": "target", "target": temp})
    rq = requestPost("/api/printer/bed", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    elif rq.status_code == 404:
        print("command not found")
        rq.close()
        return False
    else:
        rq.close()
        return False
    
def setChamberTemperature(temp):
    post_data = ujson.dumps({"command": "target", "target": temp})
    rq = requestPost("/api/printer/chamber", post_data)
    if rq.status_code == 204:
        rq.close()
        return True
    elif rq.status_code == 404:
        print("command not found")
        rq.close()
        return False
    else:
        rq.close()
        return False

def requestPost(endpoint, data):
    global octoApiKey
    global octoPrintUrl
    gc.collect()
    headers = {'Content-Type': 'application/json', 'X-Api-Key': octoApiKey}
    response = urequests.post(octoPrintUrl + endpoint, data=data, headers=headers)
    return response

def requestGet(endpoint):
    global octoApiKey
    global octoPrintUrl
    gc.collect()
    headers = {'X-Api-Key': octoApiKey}
    response = urequests.get(octoPrintUrl + endpoint, headers=headers)
    return response

class apiVersionResponse:
    def __init__(self, api,server,text):
        self.api = api
        self.server = server
        self.text = text
        
class sdStateResponse:
    def __init__(self, ready):
        self.ready = ready