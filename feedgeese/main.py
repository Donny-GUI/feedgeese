from server import WebServer

if __name__ == '__main__':
    server = WebServer(host='localhost', port=8000)
    server.start()