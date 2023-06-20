
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class Website:
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        self.jpgs  = {}
        self.pngs  = {}
        self.css   = {}
        self.htmls = {}
        self.gifs  = {}
        self.maps = [self.gifs, self.pngs, self.jpgs, self.css, self.htmls]
        self.tags = [".gif", ".png", ".jpg", ".css", ".html"]
        for root, dirs, files in os.walk(self.cwd):
            for file in files:
                for i in range(0, 5):
                    t = self.tags[i]
                    if file.endswith(t):
                        self.maps[i][file] = os.path.join(root, file)
                        break
        
    def match_path(self, filename: str):
        filename = filename[1:]
        print(filename)
        extension = os.path.splitext(filename)[1]
        print(extension)
        i = self.tags.index(extension)
        try:
            return self.maps[i][filename]
        except:
            return self.maps[-1]["index.html"]
                    
                        
                        
class Server(HTTPServer):
    def __init__(self, server_address: str="127.0.0.1", port: int=8080, bind_and_activate: bool = True) -> None:
        server_addr = (server_address, port)
        self.request_handler = Handler
        super().__init__(server_addr, self.request_handler, bind_and_activate)
        print(f"https://{server_address}:{port}")
        self.serve_forever()
        

class Handler(BaseHTTPRequestHandler):
    content = Website()
        
    def do_GET(self):
        print(self.path)
        self.path = str(self.content.match_path(self.path))
        try:
            if self.path.endswith(".html"):
                # Serve HTML files
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(self.path, 'rb', encoding='ascii') as file:
                    self.wfile.write(file.read())
            elif self.path.endswith(".css"):
                # Serve CSS files
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                with open(self.path, 'rb', encoding='ascii') as file:
                    self.wfile.write(file.read())
            elif self.path.endswith(".gif"):
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                with open(self.path, 'rb', encoding='ascii') as file:
                    self.wfile.write(file.read())
            elif self.path.endswith(".png"):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(self.path, 'rb', encoding='ascii') as file:
                    self.wfile.write(file.read())
            else:
                # Handle other file types or 404 Not Found
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
        except IOError:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')
            
server = Server()
            
