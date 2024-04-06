from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket
import json
from datetime import datetime
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/message.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('message.html', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('style.css', 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/logo.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('logo.png', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')
        parsed_data = parse_qs(post_data)
        username = parsed_data['username'][0]
        message = parsed_data['message'][0]
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        process_message(username, message)

def process_message(username, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', 5000)
        data = {
            "username": username,
            "message": message
        }
        data_json = json.dumps(data)
        s.sendto(data_json.encode(), server_address)
        s.close()
    except Exception as e:
        print("Error:", e)

def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

def run_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 5000))
    while True:
        data, address = server_socket.recvfrom(1024)
        data_json = json.loads(data.decode())
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with open('storage/data.json', 'a') as f:
            json.dump({current_time: data_json}, f)
            f.write('\n')

if __name__ == '__main__':
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()

    socket_thread = threading.Thread(target=run_socket_server)
    socket_thread.start()