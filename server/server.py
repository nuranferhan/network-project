import socket
import pickle
from _thread import start_new_thread
from server.game import Game

server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((server, port))
s.listen()

print("Sunucu dinleniyor...")

game = Game()
player_count = 0

def client_thread(conn, player_id):
    conn.send(pickle.dumps(player_id))

    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            if not data:
                break

            game.update_player(player_id, data)
            reply = game.get_all_data()
            conn.send(pickle.dumps(reply))

        except:
            break

    print(f"Player {player_id} bağlantısı koptu.")
    conn.close()

def run_server():
    global player_count
    while True:
        conn, addr = s.accept()
        print(f"Bağlantı kuruldu: {addr}")
        start_new_thread(client_thread, (conn, player_count))
        player_count += 1
