import sys
import pickle
from network import Network
from player import Player
from graphics import redraw_window
from roles import role_to_color
from scoreboard import Scoreboard
from boosts import BoostManager
from map import create_maze_wall_rects
from gameconfig import *

# --- Pygame Kurulumu ---
pygame.init()
width = MAZE_COLS * CELL_SIZE
height = MAZE_ROWS * CELL_SIZE + GAMEBAR_HEIGHT
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("THIEF COP")


def main():
    pygame.mixer.music.load("assets/bg_sound.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "Player"

    fogbool = True
    run = True
    clock = pygame.time.Clock()
    walls = []
    player1 = None
    other_players = []
    time_left = None
    game_over = False
    boost_manager = None
    message = "Connecting..."
    final_scores_data = None  # For final scoreboard

    # Skor takibi için değişkenler
    current_score = 0
    server_high_score = 0  # Serverdan gelen en yüksek skor
    server_high_score_username = ""  # Serverdan gelen en yüksek skoru yapan oyuncu

    # Güçlendirme senkronizasyonu için değişkenler
    server_boosts = []
    active_boosts = {}
    last_collected_boost = None
    last_score_sync = 0  # Son skor sync zamanını takip etmek için

    #server_ip = "192.168.1.133"
    server_ip = "127.0.0.1"
    server_port = 5555
    network = Network(server_ip, server_port)

    initial_data = network.connect()

    if initial_data and isinstance(initial_data, dict):
        message = "Waiting for opponent..."

        try:
            maze_grid = initial_data['maze']
            start_pos = initial_data['start_pos']
            role = initial_data['role']
            scoreboard = Scoreboard(username, role, score=0)

            # Başlangıçta server'dan en yüksek skoru al
            if 'high_score' in initial_data:
                server_high_score = initial_data['high_score']
                server_high_score_username = initial_data.get('high_score_username', "")

            # Sunucu tarafından oluşturulan güçlendirmeleri al
            if 'boosts' in initial_data:
                server_boosts = initial_data['boosts']
                # Tüm güçlendirmeleri aktif olarak başlat
                for boost in server_boosts:
                    active_boosts[boost['id']] = True

                # Portalların var olup olmadığını kontrol et
                portal_types = [boost['type'] for boost in server_boosts
                                if boost['type'] in ['portal1', 'portal2']]
                print(f"Alınan portal türleri: {portal_types}")

            if not maze_grid or not start_pos:
                raise ValueError("Geçersiz ilk veri alındı.")

            print(f"Oyuncu rolü: {role.upper()} konumu {start_pos}")

            player1_color = role_to_color(role)
            player1 = Player(start_pos[0], start_pos[1], player1_color, role=role)  # Role parametresini ekledik

            print("Labirent alındı, duvarlar oluşturuluyor...")
            walls = create_maze_wall_rects(maze_grid)
            print(f"{len(walls)} duvar dikdörtgeni oluşturuldu.")

            # === SUNUCU GÜÇLENDİRMELERİ İLE BOOST MANAGER ===
            boost_manager = BoostManager(walls, width, height, server_boosts)

        except (KeyError, TypeError, ValueError) as e:
            print(f"İlk veriyi işlerken hata oluştu: {e}")
            message = "Veri Hatası!"
            run = False
        except Exception as e:
            print(f"Kurulum sırasında beklenmeyen hata: {e}")
            message = "Kurulum Hatası!"
            run = False

    else:
        print("Sunucuya bağlanılamadı.")
        import traceback
        traceback.print_exc()
        message = "Bağlantı Başarısız!"
        redraw_window(win, None, None, [], width, height, message,
                      high_score=server_high_score, high_score_username=server_high_score_username)
        pygame.time.wait(3000)
        run = False

    # --- Ana Oyun Döngüsü ---
    while run:
        clock.tick(60)  # Oyunun FPS değeri
        opponent_connected = False

        if player1:
            # Güçlendirme çarpışmalarını kontrol et
            collected_boost_id = boost_manager.check_collision(player1, scoreboard)

            # Her puan değişiminde server'a bildir (saniyede en fazla 1 kez)
            current_time = pygame.time.get_ticks()
            if scoreboard and scoreboard.score != current_score and current_time - last_score_sync > 1000:
                current_score = scoreboard.score
                last_score_sync = current_time

                # Skor mesajını formatlayıp gönder
                score_message = f"score|{current_score}|{username}"
                score_reply = network.send(score_message, raw=True)

                if score_reply:
                    try:
                        score_data = pickle.loads(score_reply)
                        if 'high_score' in score_data:
                            server_high_score = score_data['high_score']
                            server_high_score_username = score_data.get('high_score_username', "")
                            print(
                                f"Sunucudan güncellenen yüksek skor: {server_high_score} yapan: {server_high_score_username}")
                    except Exception as e:
                        print(f"Skor yanıtını işlerken hata: {e}")

            # Ağ mesajını formatla - toplanmış güçlendirme ve animasyon bilgisini ekle
            if collected_boost_id:
                pos_str = f"{int(player1.x)},{int(player1.y)},{player1.direction},{player1.moving}|{collected_boost_id}"
            else:
                pos_str = f"{int(player1.x)},{int(player1.y)},{player1.direction},{player1.moving}"

            reply = network.send(pos_str, raw=True)
            if reply:
                try:
                    payload = pickle.loads(reply)

                    """eklendi: oyun bitmemişse mevcut döngüden devam edecek :18.05.2025"""
                    if "new_game" in payload and payload["new_game"]:
                        print("Yeni oyun başlatılıyor!")
                        # Yeni oyun bilgilerini al
                        start_pos = payload["start_pos"]
                        role = payload["role"]
                        server_boosts = payload["boosts"]
                        game_round = payload.get("game_round", 0)  # Tur sayısını al

                        # Oyuncu rolünü ve konumunu güncelle
                        player1_color = role_to_color(role)
                        player1 = Player(start_pos[0], start_pos[1], player1_color, role=role)

                        # Skoru güncelle (username'i koru)
                        scoreboard = Scoreboard(username, role, score=scoreboard.score if scoreboard else 0)

                        # Boost manager'ı güncelle
                        active_boosts = {}
                        for boost in server_boosts:
                            active_boosts[boost['id']] = True
                        boost_manager = BoostManager(walls, width, height, server_boosts)

                        # Oyun durumlarını sıfırla
                        game_over = False
                        fogbool = True
                        message = f"Tur {game_round}: Oyun Başlıyor!"

                        # !!! EN ÖNEMLİ DÜZELTME: Önceki oyunun skor tablosu verisini temizle !!!
                        final_scores_data = None

                        # Yüksek skor bilgilerini güncelle
                        if 'high_score' in payload:
                            server_high_score = payload['high_score']
                            server_high_score_username = payload.get('high_score_username', "")

                        # Devam et
                        continue

                    """eklendi: oyun sonu verisini işleme; oyun sonu scoreboard için; 16.05.2025"""
                    # === OYUN SONU VERİSİNİ İŞLEME BAŞLANGICI ===
                    if "game_over" in payload and payload["game_over"]:
                        final_scores_data = payload["player_scores"]
                        new_timer=payload['new_timer']

                        print("Oyun bitti, skorlar alındı:", final_scores_data)
                        message = "Oyun Bitti! Skorlar hesaplanıyor..."
                        showing_scoreboard = True
                        scoreboard_start_time = pygame.time.get_ticks()
                        temp_clock = pygame.time.Clock()

                        while showing_scoreboard:
                            redraw_window(win, player1, other_players, walls, width, height, message,
                                          scoreboard=scoreboard, timer=new_timer, boost_manager=boost_manager,
                                          fog_bool=fogbool, high_score=server_high_score,
                                          high_score_username=server_high_score_username,
                                          final_scores_data=final_scores_data)

                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    showing_scoreboard = False
                                    run = False  # tek tur döngüsü olmaması için : 18.05.2025
                            if pygame.time.get_ticks() - scoreboard_start_time > 1000:
                                showing_scoreboard = False
                                message = "Yeni oyun için hazırlanıyor..."  # Beklerken mesaj göster : 18.05.2025
                            temp_clock.tick(60)

                        continue
                    # === OYUN SONU VERİSİNİ İŞLEME BİTİŞİ ===

                    players_info = payload.get("players", [])
                    time_left = payload.get("time_left", None)
                    caught = payload.get("caught", False)

                    # Güncel yüksek skor bilgisini al
                    if 'high_score' in payload:
                        server_high_score = payload['high_score']
                        server_high_score_username = payload.get('high_score_username', "")

                    # Aktif güçlendirmeleri sunucudan güncelle
                    if "active_boosts" in payload:
                        new_active_boosts = payload["active_boosts"]
                        boost_manager.update_active_boosts(new_active_boosts)

                    # Güçlendirme toplama bilgilerini işle
                    if "collected_boost" in payload:
                        boost_info = payload["collected_boost"]
                        boost_id = boost_info["id"]
                        boost_type = boost_info["type"]

                        # Eğer bu istemci güçlendirmeyi topladıysa, etkileri uygula
                        if collected_boost_id == boost_id:
                            boost_manager.apply_boost_effect(player1, boost_type, scoreboard)

                    other_players = []
                    for p_info in players_info:
                        # Animasyon bilgileri ile birlikte oyuncu oluştur
                        if len(p_info) == 4:  # pos, role, direction, moving
                            pos, role, direction, moving = p_info
                            px, py = pos
                            color = role_to_color(role)
                            other = Player.from_absolute_pos(px, py, color, role=role,
                                                            direction=direction, moving=moving)
                            other_players.append(other)
                            opponent_connected = True
                        else:  # Eski format için geriye dönük uyumluluk
                            pos, role = p_info[:2]
                            px, py = pos
                            color = role_to_color(role)
                            other = Player.from_absolute_pos(px, py, color, role=role)
                            other_players.append(other)
                            opponent_connected = True

                    if opponent_connected and message == "Waiting for opponent...":
                        message = None
                except Exception as e:
                    print(f"Ağ yanıtını işlerken hata: {e}")
                    message = "Ağ Hatası"
            else:
                print("Ağ gönderme/alma başarısız. Bağlantı kesiliyor.")
                message = "Bağlantı Kesildi!"
                run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Çıkış olayı algılandı.")
                run = False

        if not game_over and caught:
            game_over = True
            fogbool = False
            # Yakalandığında zamanlayıcıyı durdur
            network.send("stop_timer", raw=True)

            # Hata düzeltmesi için debuglama
            print(f"Oyun sonu - Rol: {role}, Player role: {player1.role if player1 else 'Unknown'}")

            # Player1'in rolünü kontrol et, sunucudan gelen rol değişmiş olabilir
            player_role = player1.role if player1 else role

            if player_role == 'thief':
                message = f'YOU GOT CAUGHT!!!\nThe Best Score: {server_high_score} ({server_high_score_username})'
            elif player_role == 'cop':
                message = f'YOU CAUGHT THE GUY!!!\nThe Best Score: {server_high_score} ({server_high_score_username})'

        # Oyuncu hareketini sadece süre varsa işleme al
        if player1 and not game_over and time_left and 120>time_left> 0:
            player1.move(walls)
            player1.update()  # <-- güçlendirme süresi kontrol

        if not game_over and time_left == 0:
            game_over = True
            fogbool = False
            # Süre dolduğunda zamanlayıcıyı durdur
            network.send("stop_timer", raw=True)

            if role == 'thief':
                message = f'You Escaped Successfully!\nThe Best Score: {server_high_score} ({server_high_score_username})'
            elif role == 'cop':
                message = f'The guy got away!\nThe Best Score:" {server_high_score} ({server_high_score_username})'

        if not opponent_connected and message == "Waiting for opponent...":
            current_message = message
        elif game_over:
            current_message = message
        else:
            current_message = None

        redraw_window(win, player1, other_players, walls, width, height, current_message,
                      scoreboard=scoreboard, timer=time_left, boost_manager=boost_manager,
                      fog_bool=fogbool, high_score=server_high_score,
                      high_score_username=server_high_score_username,
                      final_scores_data=final_scores_data)

    print("Oyun döngüsünden çıkılıyor.")
    network.disconnect()
    pygame.quit()
    print("Pygame kapatıldı.")
    sys.exit()


if __name__ == "__main__":
    main()