import pygame

# --- Oyun Ekranı Ayarları ---
WIDTH = 720  # Pencere genişliği
HEIGHT = 650  # Pencere yüksekliği
FPS = 120  # Ana ekran FPS değeri
# clock.tick(60) Oyunun FPS değeri

# --- Oyun Bilgi Çubuğu Ayarları ---
GAMEBAR_HEIGHT = 50  # Üstteki oyun bilgi çubuğunun yüksekliği

# --- Zamanlayıcı ---
GAME_TIMER_SECONDS = 120  # Oyun süresi (saniye)
NEW_ROUND_TIMER=10

# --- Renkler ---
WHITE = (255, 255, 255)  # Beyaz
BLACK = (0, 0, 0)  # Siyah
BLUE = (0, 0, 255)  # Mavi
GREY = (26, 34, 58, 255)  # Gri
WALL_COLOR = (79, 79, 79)  # Duvarlar için gri renk

# --- Labirent Ayarları ---
MAZE_ROWS = 10  # Labirent satır sayısı
MAZE_COLS = 12  # Labirent sütun sayısı
CELL_SIZE = 60  # Hücre boyutu
WALL_THICKNESS = 8  # Duvar kalınlığı
BOOST_EDGE=CELL_SIZE*0.6 # Boost kenar boyutu
TELEPORT_COOLDOWN = 1000 # Teleport bekleme süresi

# --- Oyuncu Ayarları ---
PLAYER_WIDTH = CELL_SIZE // 3  # Oyuncu genişliği
PLAYER_HEIGHT = CELL_SIZE // 3  # Oyuncu yüksekliği
CHARACTER_WIDTH = PLAYER_WIDTH * 2  # Karakter genişliği
CHARACTER_HEIGHT = PLAYER_HEIGHT * 2  # Karakter yüksekliği
PLAYER_VELOCITY = 15  # Oyuncu hareket hızı

# --- Animasyon Ayarları ---
ANIMATION_SPEED = 0.8  # Animasyon hızı (saniye başına kare)
RADIUS = 120  # Sis efekti yarıçapı (eğer kullanılıyorsa)

# --- Yazı Tipi Ayarları ---
pygame.font.init()  # Yazı tipi sistemini başlat
MSG_FONT = pygame.font.SysFont("arial", 40)  # Genel mesajlar için yazı tipi
SCORE_FONT = pygame.font.SysFont("arial", 30)  # Oyun bilgi çubuğu skor yazı tipi
HIGH_SCORE_FONT = pygame.font.SysFont("arial", 24)  # Yüksek skor yazı tipi
TIMER_FONT = pygame.font.SysFont("arial", 30)  # Zamanlayıcı yazı tipi
# Skor ve skor tablosu için kullanılacak yazı tipleri
SCORE_FONT = pygame.font.SysFont("arial", 30)
SCOREBOARD_TITLE_FONT = pygame.font.SysFont("arial", 40, bold=True)  # Skor tablosu başlık yazı tipi
SCOREBOARD_SCORE_FONT = pygame.font.SysFont("arial", 30)  # Skor tablosu skor yazı tipi


