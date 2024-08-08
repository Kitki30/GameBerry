import network
import machine
import gc
import usocket as socket
import ujson


ALLOW_TESTS = True

routes = {}

def add_route(path, method, handler):
    if path not in routes:
        routes[path] = {}
    routes[path][method] = handler

def handle_request(path, method, body):
    if path in routes and method in routes[path]:
        return routes[path][method](body)
    else:
        return 'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 not found.'

def test_h(_):
    global ALLOW_TESTS
    if ALLOW_TESTS == True:
        return 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + "Test"


def launch():
    gc.collect()
    print("Launching setup...")
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='Gameberry-Setup')
    ap.active(True)
    while not ap.active():
        pass
    print("Connect to hotspot:\nSSID: Gameberry-setup")
    print('Network config:', ap.ifconfig())

    gc.collect()
    add_route("/test", "GET", test_h)

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected ', addr)
        request = b""
        while True:
            data = cl.recv(1024)
            if not data:
                break
            request += data
        request_str = request.decode()
        print("Request:", request_str)
        try:
            method, path, _ = request_str.split(' ', 2)
            headers, body = request_str.split('\r\n\r\n', 1)
        except ValueError:
            method, path, body = 'GET', '/', ''
        response = handle_request(path, method, body)
        cl.send(response)
        cl.close()