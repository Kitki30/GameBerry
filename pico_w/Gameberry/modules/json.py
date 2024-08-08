import ujson as json

def read(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def write(filename, data):
    with open(filename, 'wb') as file:
        json.dump(data, file)
        
def read_from_string(data):
    return json.loads(data)