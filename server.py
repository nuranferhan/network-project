import socket
from _thread import start_new_thread
import sys
import time
import pickle
from roles import shuffle_roles
from map import generate_maze_grid, find_start_positions, find_dead_end_cells
from timer import Timer
from effects import ifcatch
import random
from boosts import BOOST_TYPES
from gameconfig import *

pygame.init()

server_ip = "0.0.0.0"  # Tüm ağ arayüzlerinden bağlantı kabul et
server_port = 5555
max_clients = 3

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print("Generating maze...")
maze_grid = generate_maze_grid(MAZE_ROWS, MAZE_COLS)
try:
    start_positions = find_start_positions(maze_grid, max_clients)
    print(f"Generated {len(start_positions)} starting positions.")
except ValueError as e:
    print(f"Error generating start positions: {e}")
    sys.exit(1)

players_data = {}
roles = shuffle_roles()
timer = Timer(GAME_TIMER_SECONDS)
countdown_started = False
keyboard_thread_started = False
caught = False
eklendi=False
"""eklendi: oyunu yeniden başlatmak için değişkenler: 18.05.2025"""
game_round = 0  # Tur sayacı

# Sunucu tarafında güçlendirici (boost) yönetimi
boosts = []  # Güçlendirici konumlarını ve türlerini saklamak için liste
active_boosts = {}  # Hâlâ aktif olan güçlendiricileri izlemek için sözlük

# Yüksek skor takibi için değişkenler
high_score = 0  # En yüksek skoru tut
high_score_username = ""  # En yüksek skoru yapan kullanıcı adı

"""eklendi: Oyun Sonu Kontrolü Fonksiyonu; oyun sonundaki scoreboard için; 16.05.2025"""
def is_game_over(caught, timer):
    return caught or timer.is_finished()

"""eklendi: Oyun Sonu Verisini Hazırlama ve Gönderme Fonksiyonu; oyun sonundaki scoreboard için; 16.05.2025"""
def broadcast_game_over(conn):
    global players_data
    game_over_data = []
    for player_id, player_info in players_data.items():
        game_over_data.append({
            "username": player_info["username"],
            "score": player_info["score"],
            "role": player_info["role"]
        })
    try:
        conn.sendall(pickle.dumps({"game_over": True, "player_scores": game_over_data}))
    except socket.error as e:
        print(f"Oyun sonu verisi gönderilirken hata: {e}")

"""eklendi: oyunu yeniden başlatmak için fonksiyon: 18.05.2025"""
def reset_game():

    global players_data, roles, timer, countdown_started, caught, game_round, boosts, active_boosts,eklendi,new_timer

    # Tur sayacını artır
    game_round += 1
    print(f"\n==== YENİ OYUN TURU {game_round} BAŞLADI ====")

    # Oyuncu rollerini yeniden karıştır
    roles = shuffle_roles()

    # Zamanlayıcıyı sıfırla
    timer = Timer(GAME_TIMER_SECONDS)
    countdown_started = False
    caught = False
    eklendi = False

    # Güçlendirmeleri yeniden oluştur
    boosts = []
    active_boosts = {}
    generate_server_boosts()

    # Oyuncuların skorlarını koru ama konumlarını ve rollerini güncelle
    for player_id in list(players_data.keys()):
        if player_id < len(roles):
            players_data[player_id]['role'] = roles[player_id]
            players_data[player_id]['pos'] = start_positions[player_id]
            # Animasyon bilgilerini varsayılana döndür
            players_data[player_id]['direction'] = 'right'
            players_data[player_id]['moving'] = False

            # Yeni oyun bilgilerini gönder
            new_game_data = {
                'new_game': True,
                'start_pos': start_positions[player_id],
                'role': roles[player_id],
                'boosts': boosts,
                'high_score': high_score,
                'high_score_username': high_score_username,
                'game_round': game_round
            }
            try:
                players_data[player_id]['conn'].sendall(pickle.dumps(new_game_data))
                print(f"Player {player_id}: {roles[player_id].upper()} yeni oyun bilgisi gönderildi")
            except socket.error as e:
                print(f"Player {player_id} yeni oyun bilgisi gönderilirken hata: {e}")

    # Yeterli sayıda oyuncu bağlı ise zamanlayıcıyı başlat
    if len(players_data) >= max_clients:
        print("🎮 Yeni oyun için zamanlayıcı başlatılıyor.")
        timer.start()
        countdown_started = True

def generate_server_boosts():
    """Sunucu seviyesinde, aralarında minimum mesafe olan güçlendiriciler oluştur"""
    global boosts, active_boosts

    # Labirent boyutlarına göre genişlik ve yükseklik hesapla
    width = MAZE_COLS * CELL_SIZE
    height = MAZE_ROWS * CELL_SIZE

    # Güçlendiriciler arası minimum mesafe (piksel cinsinden)
    MIN_BOOST_SPACING = CELL_SIZE * 3  # Güçlendiriciler arasında en az 3 hücre mesafe olsun

    # Labirent ızgarasından duvar dikdörtgenlerini oluştur
    walls = []
    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            if maze_grid[row][col] == 1:  # 1 bir duvarı temsil eder
                walls.append(pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Yerleştirilen güçlendirici türlerini takip et
    placed_types = set()

    for boost_type, info in BOOST_TYPES.items():
        count = info["count"]
        placed = 0
        attempts = 0

        while placed < count and attempts < 1000:
            max_x_cells = (width - CELL_SIZE) // CELL_SIZE
            max_y_cells = (height - CELL_SIZE) // CELL_SIZE

            if boost_type != 'portal1' and boost_type != 'portal2':
                x = random.randint(0, max_x_cells) * CELL_SIZE +((CELL_SIZE-BOOST_EDGE)/2)
                y = random.randint(1, max_y_cells) * CELL_SIZE +((CELL_SIZE-BOOST_EDGE)/2)
                boost_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                # Güçlendiricinin herhangi bir duvarla çakışıp çakışmadığını kontrol et
            wall_collision = False
            for wall in walls:
                if boost_rect.colliderect(wall):
                    wall_collision = True
                    break

            if wall_collision:
                attempts += 1
                continue

            # Güçlendiricinin mevcut güçlendiricilere çok yakın olup olmadığını kontrol et
            too_close = False
            for existing_boost in boosts:
                # Merkezler arasındaki mesafeyi hesapla
                ex, ey = existing_boost["x"] + CELL_SIZE / 2, existing_boost["y"] + CELL_SIZE / 2
                nx, ny = x + CELL_SIZE / 2, y + CELL_SIZE / 2

                distance = ((ex - nx) ** 2 + (ey - ny) ** 2) ** 0.5

                if distance < MIN_BOOST_SPACING:
                    too_close = True
                    break

            if too_close:
                attempts += 1
                continue

            # Güçlendiriciyi listemize ekle
            boost_id = f"{boost_type}_{placed}"
            boost_data = {
                "id": boost_id,
                "type": boost_type,
                "x": x,
                "y": y
            }
            boosts.append(boost_data)
            active_boosts[boost_id] = True  # Bu güçlendiriciyi aktif olarak işaretle
            placed_types.add(boost_type)  # Bu türün yerleştirildiğini takip et

            placed += 1
            attempts = 0

    # --------------------------PORTAL--------------------------------
    # portal1 ve portal2'nin ikisinin de yerleştirildiğinden emin ol
    missing_portals = []
    if "portal1" not in placed_types:
        missing_portals.append("portal1")
    if "portal2" not in placed_types:
        missing_portals.append("portal2")

    print(missing_portals)

    # Eğer herhangi bir portal eksikse, zorla yerleştir
    # 2. Portalları Yerleştir
    print("\nPlacing portals...")
    portal_types_to_place = [ptype for ptype in BOOST_TYPES if "portal" in ptype.lower()]
    dead_ends = find_dead_end_cells(maze_grid)
    random.shuffle(dead_ends)

    print(f"Found {len(dead_ends)} dead ends. Attempting to place {len(portal_types_to_place)} portals.")
    # Hangi çıkmaz sokakların kullanıldığını takip etmek için:
    # print(f"Available dead ends: {dead_ends}")

    placed_portals_count = 0
    for portal_type in portal_types_to_place:
        if not dead_ends:
            print(f"Warning: No dead ends available to place {portal_type}.")
            continue

        successfully_placed_this_portal = False
        attempts_for_this_portal = 0

        available_dead_ends_for_this_portal = list(dead_ends)  # Her portal için listeyi kopyala

        while not successfully_placed_this_portal and attempts_for_this_portal < 100 and available_dead_ends_for_this_portal:
            attempts_for_this_portal += 1

            chosen_dead_end_index = random.randrange(len(available_dead_ends_for_this_portal))
            cell_row, cell_col = available_dead_ends_for_this_portal.pop(chosen_dead_end_index)

            x = cell_col * CELL_SIZE+ ((CELL_SIZE-BOOST_EDGE)/2)
            y = cell_row * CELL_SIZE + 50+ ((CELL_SIZE-BOOST_EDGE)/2)

            portal_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            too_close_or_direct_overlap = False
            for existing_boost in boosts:
                existing_rect = pygame.Rect(existing_boost["x"], existing_boost["y"], CELL_SIZE, CELL_SIZE)
                if portal_rect.colliderect(existing_rect):
                    too_close_or_direct_overlap = True
                    break
                dist_sq = ((existing_boost["x"] + CELL_SIZE / 2) - (x + CELL_SIZE / 2)) ** 2 + \
                          ((existing_boost["y"] + CELL_SIZE / 2) - (y + CELL_SIZE / 2)) ** 2
                if dist_sq < 180:  # Portallar için de aynı mesafe kuralı geçerli olsun
                    too_close_or_direct_overlap = True
                    break
            if too_close_or_direct_overlap:
                # print(f"  DEBUG ({portal_type}): Portal at dead end ({cell_row},{cell_col}) too close/collided.")
                continue

            boost_id = f"{portal_type}_0"
            boost_data = {"id": boost_id, "type": portal_type, "x": x, "y": y}
            boosts.append(boost_data)
            active_boosts[boost_id] = True

            successfully_placed_this_portal = True
            placed_portals_count += 1
            print(f"  Successfully placed {portal_type} at dead end ({cell_row},{cell_col}) -> coords ({x},{y})")

            if (cell_row, cell_col) in dead_ends:
                dead_ends.remove((cell_row, cell_col))

        if not successfully_placed_this_portal:
            print(
                f"  Warning: Could not place {portal_type} after trying {attempts_for_this_portal} dead ends or max attempts.")

    print(f"\nBoost generation complete. Total boosts generated: {len(boosts)}")

    # Portalları birbirine bağla
    _link_portals()
    print(f"Generated {len(boosts)} boosts with proper spacing")

    # Portal yerleşimini doğrula
    portal_types_present = [boost["type"] for boost in boosts if boost["type"] in ["portal1", "portal2"]]
    print(f"Portal types present: {portal_types_present}")


def _link_portals():
    """portal1 ve portal2'yi birbirine bağla"""
    portal1 = None
    portal2 = None

    # Her iki portalı da bul
    for boost in boosts:
        if boost["type"] == "portal1":
            portal1 = boost
        elif boost["type"] == "portal2":
            portal2 = boost

    # Her iki portal da varsa portal çifti bilgisini sakla
    if portal1 and portal2:
        # Sadece her iki portalın da var olduğundan emin oluyoruz
        # Asıl ışınlanma mantığı istemci tarafında ele alınacak
        print("Portal pair successfully linked")
    else:
        print("WARNING: Could not link portals - missing one or both portals")


# -------------------------------------------------------------------------------


def handle_boost_collection(player_id, boost_id):
    """Bir oyuncu bir güçlendirici topladığında işle"""
    global active_boosts

    if boost_id in active_boosts and active_boosts[boost_id]:
        # Türünü belirlemek için güçlendiriciyi bul
        collected_boost = None
        for boost in boosts:
            if boost["id"] == boost_id:
                collected_boost = boost
                break

        if collected_boost:
            boost_type = collected_boost["type"]

            # KRİTİK DÜZELTME: Portal güçlendiricilerini devre dışı bırakma
            if boost_type != "portal1" and boost_type != "portal2":
                active_boosts[boost_id] = False

            print(f"Player {player_id} collected boost {boost_id} of type {boost_type}")
            return boost_type

    return None


def string_to_pos(pos_str):
    try:
        parts = pos_str.split("|")
        if len(parts) == 1:
            # Normal pozisyon güncellemesi
            pos_data = parts[0].split(",")
            if len(pos_data) == 2:
                # Sadece x,y koordinatları
                x, y = map(int, pos_data)
                return (x, y), None, None
            elif len(pos_data) == 4:
                # x,y,direction,moving (animasyon bilgileri dahil)
                x, y, direction, moving = int(pos_data[0]), int(pos_data[1]), pos_data[2], pos_data[3] == "True"
                return (x, y), None, (direction, moving)
        elif len(parts) == 2:
            # Güçlendirici toplama ile pozisyon güncellemesi
            pos_part, boost_part = parts
            pos_data = pos_part.split(",")
            if len(pos_data) == 2:
                x, y = map(int, pos_data)
                return (x, y), boost_part, None
            elif len(pos_data) == 4:
                x, y, direction, moving = int(pos_data[0]), int(pos_data[1]), pos_data[2], pos_data[3] == "True"
                return (x, y), boost_part, (direction, moving)
    except:
        pass
    return (0, 0), None, None


# Yeni fonksiyon: Skor güncellemesi için
def update_high_score(player_id, score, username):
    global high_score, high_score_username

    if score > high_score:
        high_score = score
        high_score_username = username
        print(f"New high score: {high_score} by {high_score_username}")
        return True
    return False


def threaded_client(conn, player_id):
    global players_data, high_score, high_score_username, eklendi, new_timer
    print(f"Sending initial data to Player {player_id}...")

    initial_data = {
        'maze': maze_grid,
        'start_pos': start_positions[player_id],
        'role': roles[player_id],
        'boosts': boosts,  # İstemciye tüm güçlendirici verilerini gönder
        'high_score': high_score,  # Mevcut yüksek skoru gönder
        'high_score_username': high_score_username  # Yüksek skoru yapan kullanıcı adını gönder
    }

    try:
        conn.sendall(pickle.dumps(initial_data))
        print(f"Player {player_id}: {roles[player_id].upper()} connected")
    except socket.error as se:
        print(f"Error sending initial data to Player {player_id}: {se}")
        if player_id in players_data:
            del players_data[player_id]
        conn.close()
        return

    # --- Veri alışverişi döngüsü ---
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print(f"Player {player_id} disconnected.")
                break

            # Bu bir skor güncelleme mesajı mı kontrol et
            data_str = data.decode("utf-8")

            # Skor güncelleme formatı: "score|[score]|[username]"
            if data_str.startswith("score|"):
                parts = data_str.split("|")
                if len(parts) >= 3:
                    try:
                        player_score = int(parts[1])
                        player_username = parts[2]

                        # Gerekirse yüksek skoru güncelle
                        score_updated = update_high_score(player_id, player_score, player_username)

                        if player_id in players_data:
                            players_data[player_id]['score'] = player_score
                            players_data[player_id]['username'] = player_username

                        print(f"Player {player_id} ({player_username}) score: {player_score}")

                        # Güncel yüksek skor ile onay gönder
                        conn.sendall(pickle.dumps({
                            'high_score': high_score,
                            'high_score_username': high_score_username
                        }))
                        continue
                    except ValueError:
                        print(f"Invalid score format received: {data_str}")

            # Normal pozisyon güncellemesi
            received_pos, boost_id, animation_data = string_to_pos(data_str)

            # Eğer bir güçlendirici ID'si gönderildiyse güçlendirici toplamayı işle
            collected_boost_type = None
            if boost_id:
                collected_boost_type = handle_boost_collection(player_id, boost_id)

            # Eğer oyuncunun bilgisi eksikse, yeniden oluştur
            if player_id not in players_data:
                players_data[player_id] = {
                    'pos': received_pos,
                    'conn': conn,
                    'addr': None,
                    'role': roles[player_id],
                    'score': 0,
                    'username': 'Player',
                    'direction': 'right',  # Varsayılan yön
                    'moving': False  # Varsayılan hareket durumu
                }
            else:
                players_data[player_id]['pos'] = received_pos
                # Animasyon verisi varsa güncelle
                if animation_data:
                    players_data[player_id]['direction'] = animation_data[0]
                    players_data[player_id]['moving'] = animation_data[1]

            # Diğer oyunculara ait bilgileri derle (animasyon bilgilerini de ekleyerek)
            other_players = [
                (pdata['pos'], pdata['role'], pdata.get('direction', 'right'), pdata.get('moving', False))
                for pid, pdata in players_data.items()
                if pid != player_id
            ]
            caught = ifcatch(players_data)

            payload = {
                'players': other_players,
                'time_left': timer.get_time_left(),
                'caught': caught,
                'active_boosts': active_boosts,  # Tüm güçlendiricilerin güncel durumunu gönder
                'high_score': high_score,  # Güncel yüksek skoru gönder
                'high_score_username': high_score_username  # Yüksek skoru yapan kullanıcı adını gönder
            }

            if collected_boost_type:
                payload['collected_boost'] = {
                    'id': boost_id,
                    'type': collected_boost_type
                }

            """düzeltme amaçlı yorum satırında/ 16.05.2025"""
            # conn.sendall(pickle.dumps(payload))

            """ eklendi: Oyun Sonu Kontrolü Fonksiyonu; oyun sonundaki scoreboard için; 16.05.2025"""
            # === OYUN SONU KONTROLÜ VE SKOR GÖNDERİMİ ===
            if is_game_over(caught, timer):
                print("Oyun bitti!")

                if caught and not eklendi:
                    eklendi=True
                    for pid,data in players_data.items():
                        role = data['role']
                        if role == 'cop':
                            data['score']+=20
                    new_timer = Timer(NEW_ROUND_TIMER)
                    new_timer.start()
                elif timer.is_finished() and not eklendi:
                    eklendi=True
                    for pid,data in players_data.items():
                        role = data['role']
                        if role == 'thief':
                            data['score']+=30
                    new_timer = Timer(NEW_ROUND_TIMER)
                    new_timer.start()


                game_over_data = []
                for pid, pdata in players_data.items():
                    game_over_data.append({
                        'username': pdata['username'],
                        'score': pdata['score'],
                        'role': pdata['role'],
                    })
                payload['game_over'] = True
                payload['player_scores'] = game_over_data
                payload['new_timer']= new_timer.get_time_left()
                """eklendi : oyun sonundaki akışın yeni tur için devam etmesi :18.05.2025"""
                payload['game_round'] = game_round
                conn.sendall(pickle.dumps(payload))


                # 5 saniye bekle (skorboard gösterimi için)
                #time.sleep(5)

                # Eğer hala yeteri kadar oyuncu bağlıysa yeni oyunu başlat
                if len(players_data) == max_clients and new_timer.get_time_left()==0:
                    time.sleep(5) # oyun sonu çakışması engellenmesi için 19.05.2025
                    reset_game()

                # Oyunu sonlandırma ve threaded_client fonksiyonundan çıkma kısmını iptal ediyoruz
                # (break yerine continue kullanarak döngüye devam ediyoruz)
                continue  # break yerine continue kullanıyoruz
            else:
                conn.sendall(pickle.dumps(payload))  # normal akış

        except socket.error as ee:
            print(f"Socket Error with Player {player_id}: {ee}")
            break
        except Exception as s:
            print(f"General Error with Player {player_id}: {s}")
            break

    try:
        del players_data[player_id]
        print(f"Remaining players: {list(players_data.keys())}")
    except KeyError:
        print(f"Player {player_id} already removed.")
    conn.close()


# Sunucuyu başlatmadan önce güçlendiricileri oluştur
generate_server_boosts()

# --- Sunucu Başlat ---
try:
    server_socket.bind((server_ip, server_port))
    print(f"Server binding successful ({server_ip}:{server_port}).")
except socket.error as e:
    print(f"Server binding failed: {str(e)}")
    sys.exit()

try:
    server_socket.listen(max_clients)
    print("Server started. Waiting for connections...")
except socket.error as e:
    print(f"Server listen failed: {str(e)}")
    server_socket.close()
    sys.exit()

# --- Bağlantı Kabul Döngüsü ---
while True:
    try:
        conn, addr = server_socket.accept()
        print(f"Connected to: {addr}")

        assigned_id = -1
        for i in range(max_clients):
            if i not in players_data:
                assigned_id = i
                break

        if assigned_id == -1:
            print("Server is full. Rejecting connection.")
            conn.sendall(pickle.dumps("Server full"))
            conn.close()
            continue

        # İlk pozisyonu önceden kaydet!
        players_data[assigned_id] = {
            'pos': start_positions[assigned_id],
            'conn': conn,
            'addr': addr,
            'role': roles[assigned_id],
            'score': 0,
            'username': 'Player',
            'direction': 'right',  # Varsayılan yön
            'moving': False  # Varsayılan hareket durumu
        }

        start_new_thread(threaded_client, (conn, assigned_id))
        print(f"Thread started for Player {assigned_id}.")
        print(f"Current players: {list(players_data.keys())}")

        # 3 oyuncu bağlanınca sayaç başlat
        if not countdown_started and len(players_data) == max_clients:
            print("🎮 3 oyuncu bağlandı, sayaç başlatılıyor.")
            timer.start()
            countdown_started = True


    except KeyboardInterrupt:
        print("\nServer shutting down...")
        break
    except Exception as e:
        print(f"Error accepting connection: {e}")

print("Closing server socket.")
server_socket.close()