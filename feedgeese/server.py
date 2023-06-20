import socket
import os
import multiprocessing
import time


INDEX_HTML_TAG = "GET / HTTP/1.1"
INDEX_CSS_TAG = "GET /index.css HTTP/1.1"
HTML_CONTENT_TYPE = "Content-Type: text/html\r\n"
CSS_CONTENT_TYPE = "Content-Type: text/css\r\n"
PNG_CONTENT_TYPE = "Content-Type: image/png\r\n"
GIF_CONTENT_TYPE = "Content-Type: image/gif\r\n"
HEADER_200_OK = "HTTP/1.1 200 OK\r\n"
HEADER_302_FOUND = "HTTP/1.1 302 Found\r\n"
RN = "\r\n"


class MultiProcessSafePrint:
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    clear = "\033[0m"
    def __init__(self) -> None:
        self.start_time = time.time()
    
    def print(self, title:str="SERVER", message:str=""):
        t = str(time.time())
        if title in ("SERVER", "STARTED"):
            color = self.blue
        elif title in ("REQUEST", "FOUND", "CONNECTED"):
            color = self.green
        elif title in ("FINISHED", "DISCONNECTED"):
            color = self.red
        else:
            color = self.yellow
        
        msg =  "\n " + color + "[ " + title + " ]" + self.clear + ": " +  message
        print(msg, end="")

class WebContent:
    def __init__(self, filepath: str) -> None:
        
        self._filepath = filepath
        self._filename = os.path.basename(self.filepath)
        self._extension = os.path.splitext(self.filename)[1]
        with open(self._filepath, "rb") as rfile:
            self._content = rfile.read()
    
    @property
    def content(self):
        return self._content

    @property
    def filepath(self):
        return self._filepath

    @property
    def filename(self):
        return self._filename

    @property
    def extension(self):
        return self._extension

class WebsiteContent:
    content_map = {".png": PNG_CONTENT_TYPE, ".gif": GIF_CONTENT_TYPE, ".css":CSS_CONTENT_TYPE, ".html":HTML_CONTENT_TYPE} 
    def __init__(self) -> None:
        self.printer = MultiProcessSafePrint()
        self.cwd = os.getcwd()
        
        self.html_file_map = {}
        self.css_file_map = {}
        self.gif_file_map = {}
        self.image_file_map = {}
        
        self._file_extensions = [".html", ".css", ".png", ".gif"]
        self._file_map: dict[str: WebContent] = {}
        
        self.printer.print("STARTED", "processes")
        for root, dirs, files in os.walk(self.cwd):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                self.printer.print("FOUND", dir_path)
                self.search_directory(dir_path)
                #multiprocessing.Process(target=self.search_directory, args=(dir_path, )).start()
            
    def search_directory(self, dir_path: str):
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                for ext in self._file_extensions:
                    if file.endswith(ext):
                        _path = os.path.join(root, file)
                        self.printer.print("FOUND", _path)
                        self._file_map[file] = WebContent(_path)
                        break
        self.printer.print("FINISHED", dir_path)
        
    
    def get_content(self, filename: str):
        return str(self._file_map[filename].content)

    def content_type(self, filename: str):
        ext = os.path.splitext(filename)[1]
        return self.content_map[ext]
        
        
        
   
class WebServer:
    
    def __init__(self, host='127.0.0.1', port=8080):
        self.web_content = WebsiteContent()
        self.p  = MultiProcessSafePrint()
        
        self.host = host
        self.port = port
        self.cwd = os.getcwd()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.valid_credentials = {
            'admin': 'password123',
            'user': '123456'
        }
    
    #/////////////////////////////////////////
    #   initializing
    #/////////////////////////////////////////    

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.p.print("STARTED", f"http://{self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.p.print("CONNECTED", f"{client_address[0]}:{client_address[1]}")
            self.handle_request(client_socket)
            client_socket.close()
    
    #/////////////////////////////////////////
    #   Handling
    #/////////////////////////////////////////

    def handle_request(self, client_socket):
        request = client_socket.recv(1024).decode('utf-8')
        self.p.print("REQUEST", request)
        response = self.generate_response(request)
        client_socket.sendall(response.encode())

    def handle_login_request(self, request):
        response_body = ""
        status_line = HEADER_200_OK
        response_headers = HTML_CONTENT_TYPE
        
        if 'username' in request and 'password' in request:
            username = self.extract_form_data(request, 'username')
            password = self.extract_form_data(request, 'password')
            if self.validate_credentials(username, password):
                status_line = HEADER_302_FOUND
                response_headers += "Location: index.html\r\n"
            else:
                response_body = "<h1>Invalid credentials. Please try again.</h1>"
        else:
            response_body = self.read_file_content('login.html')
        
        response = f"{status_line}{response_headers}\r\n{response_body}"
        
        return response
    
    def handle_index_request(self):
        headers = HEADER_200_OK
        body = self.web_content.get_content("index.html")
        headers+=self.web_content.content_type("index.html")
        return headers + body
        
    def generate_response(self, request):
        response = ""
        
        # Extract the requested file path from the request
        file_path = self.get_file_path(request)
        self.p.print(f"REQUEST", file_path)
        
        
        # Check if the requested file is the pages
        if request.startswith("GET / HTTP/1.1"):
            self.handle_index_request()
        if file_path == 'login.html':
            response = self.handle_login_request(request)
        
        elif file_path == "index.html":
            response = self.handle_index_request(file_path)
        
        else:
            pass
        
        return response
            
    def get_file_path(self, request):
        # Extract the requested file path from the request
        lines = request.split(RN)
        file_path = lines[0].split(' ')[1].lstrip('/')
        return file_path

    def extract_form_data(self, request, field):
        # Extract the value of a form field from the request
        lines = request.split(RN)
        form_data_line = [line for line in lines if line.startswith(f'{field}=')][0]
        value = form_data_line.split('=')[1]
        return value

    def validate_credentials(self, username, password):
        # Check if the provided credentials are valid
        return username in self.valid_credentials and self.valid_credentials[username] == password

    def read_file_content(self, file_path):
        # Read the contents of a file
        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()
            return file_contents
        except FileNotFoundError:
            return "404 Not Found"


if __name__ == "__main__":
    multiprocessing.freeze_support()
    web_server = WebServer(port=8080)
    web_server.start()