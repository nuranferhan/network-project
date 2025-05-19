import socket
import pickle

class Network:
    def __init__(self, server_ip, server_port):
        """Ağ bağlantı yöneticisini başlatır."""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = server_port
        self.addr = (self.server, self.port)
        self.initial_data = None  # {'maze': grid, 'start_pos': (x,y)} verisini saklayacak

    def connect(self):
        """Sunucuya bağlanır ve ilk labirent ve başlangıç verilerini alır."""
        try:
            print(f"{self.addr} adresine bağlanmaya çalışılıyor...")
            self.client.connect(self.addr)
            print("Bağlantı kuruldu. İlk veriler bekleniyor...")
            # İlk veri paketini al (4096 bayta kadar, labirent çok büyükse artırılabilir)
            # Veri büyükse parça parça alınmalı
            data = b""
            while True:
                chunk = self.client.recv(4096)
                if not chunk:
                    # Sunucu bağlantıyı hemen kapatırsa olabilir
                    raise socket.error("Bağlantı sunucu tarafından erken kesildi.")
                data += chunk
                try:
                    # Unpickle etmeyi dene. Başarılıysa büyük ihtimalle tüm veri alındı.
                    # Bu basitleştirilmiş bir yöntemdir; daha sağlamı,
                    # önce verinin boyutunu göndermek olurdu.
                    self.initial_data = pickle.loads(data)
                    print("İlk veriler alındı ve ayrıştırıldı.")
                    return self.initial_data  # Sözlüğü döndür
                except pickle.UnpicklingError:
                    # Veri eksik, alım devam etsin
                    print("Veri alımı devam ediyor...")
                    continue
                except EOFError:
                    raise socket.error("Veri alımı sırasında bağlantı kesildi.")

        except socket.error as e:
            print(f"Bağlantı Hatası: {e}")
            self.initial_data = None
            return None  # Bağlantı hatasını bildir
        except pickle.UnpicklingError as e:
            print(f"İlk verileri alırken Pickle hatası: {e}")
            self.initial_data = None
            self.disconnect()  # Bozuk bağlantıyı kapat
            return None
        except Exception as e:
            print(f"Bağlantı sırasında beklenmeyen bir hata oluştu: {e}")
            self.initial_data = None
            self.disconnect()
            return None

    def send(self, data_str, raw=False):
        """Sunucuya string veri (oyuncu konumu) gönderir ve cevabı döndürür."""
        try:
            self.client.sendall(str.encode(data_str))
            reply = self.client.recv(4096)
            return reply if raw else reply.decode('utf-8')
        except socket.error as e:
            print(f"Gönderme/Alma Hatası: {e}")
            # Gerçek bir oyunda burada yeniden bağlantı denenebilir
            return None  # Başarısızlığı bildir
        except Exception as e:
            print(f"Gönderme/alma sırasında beklenmeyen bir hata oluştu: {e}")
            return None

    def disconnect(self):
        """İstemci soketini kapatır."""
        try:
            print("İstemci soketi kapatılıyor...")
            self.client.close()
        except socket.error as e:
            print(f"Soket kapatma hatası: {e}")
        except Exception as e:
            print(f"Bağlantı kapatma sırasında beklenmeyen hata: {e}")

    # İsteğe bağlı: Başlangıç pozisyonu dışarıdan erişilmek istenirse
    def get_start_pos(self):
        return self.initial_data.get('start_pos', None) if self.initial_data else None
