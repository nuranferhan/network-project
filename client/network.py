# Sunucuyla bağlantıyı sağlar
import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"  # Gerekirse IP ile değiştirilebilir
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = None
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.player_id = pickle.loads(self.client.recv(2048))
        except Exception as e:
            print("Sunucuya bağlanılamadı:", e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print("Gönderim hatası:", e)
            return None
