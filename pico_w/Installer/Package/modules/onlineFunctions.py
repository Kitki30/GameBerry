import modules.requests as requests
import ujson
import machine
import uos


server = 'gameberry.kitki30.tk' # Official gameberry servers
protocol = 'https://'

def getMachineName():
    return uos.uname().machine

def getUniqueID():
    unique_id = machine.unique_id()
    unique_id_str = ''.join(['{:02x}'.format(b) for b in unique_id])
    return unique_id_str

def register():
    post_data = ujson.dumps({ 'id': str(getUniqueID()), 'name': str(getMachineName())})
    try:
        request = requests.POST(protocol+server+"/register", post_data)
        print(request.text)
        if request['code'] == 0:
            text = request.text
            request.close()
            return text        
        request.close()
        
    except OSError as err:
        print("Activation error!")
        print(err)
        return "No"
register()