# Socket bağlantılarını dinler ve yönetir
import socket
import json

class Network:
    def __init__(self, server_ip="127.0.0.1", server_port=12345):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))

    def send_data(self, data):
        self.client_socket.send(json.dumps(data).encode())

    def receive_data(self):
        response = self.client_socket.recv(1024)
        return json.loads(response.decode())
