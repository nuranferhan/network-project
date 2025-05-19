import pygame
import json
import os
import subprocess
import re
import sys

# --- Pygame HomeScreen Ayarları ---
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THIEF COP")

# --- FPS ve zamanlama ---
clock = pygame.time.Clock()
FPS = 60

# --- GIF karelerini yükle ---
bg_frames = []
bg_folder = "homescreen-bgif"

def extract_frame_number(filename):
    match = re.search(r'frame_(\d+)', filename)
    return int(match.group(1)) if match else -1

files = sorted(
    [f for f in os.listdir(bg_folder) if f.endswith(".gif")],
    key=extract_frame_number
)

for filename in files:
    path = os.path.join(bg_folder, filename)
    frame = pygame.image.load(path).convert()
    frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))
    bg_frames.append(frame)

current_frame = 0
frame_counter = 0
frame_delay_ticks = int(0.05 * FPS)

# --- Logo yükle (isteğe bağlı) ---
try:
    LOGO = pygame.image.load("assets/logo.png")
    LOGO = pygame.transform.scale(LOGO, (100, 100))
except:
    LOGO = None

# --- Ses simgeleri ---
try:
    SOUND_ON_IMG = pygame.image.load("assets/sound_on.png")
    SOUND_ON_IMG = pygame.transform.scale(SOUND_ON_IMG, (50, 50))
    SOUND_OFF_IMG = pygame.image.load("assets/sound_off.png")
    SOUND_OFF_IMG = pygame.transform.scale(SOUND_OFF_IMG, (50, 50))
except:
    SOUND_ON_IMG = SOUND_OFF_IMG = None

# --- Exit simgesi ---
try:
    EXIT_IMG = pygame.image.load("assets/exit.png")
    EXIT_IMG = pygame.transform.scale(EXIT_IMG, (50, 50))
except:
    EXIT_IMG = None

# --- Fontlar ve renkler ---
FONT_TITLE = pygame.font.SysFont("arial", 40, bold=True)
FONT_SUB = pygame.font.SysFont("arial", 22)
FONT_INPUT = pygame.font.SysFont("arial", 20)
FONT_BUTTON = pygame.font.SysFont("arial", 24)
COLOR_INACTIVE = pygame.Color('gray')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_TEXT = pygame.Color('white')

# --- Ses ve müzik ayarları ---
pygame.mixer.music.load("assets/background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
music_muted = False
music_paused = False

# --- State değişkenleri ---
username = ''
active = False
show_rules = False
show_options = False

# --- Butonlar ---
input_box = pygame.Rect(300, 420, 200, 40)
input_color = COLOR_INACTIVE
button_play = pygame.Rect(325, 480, 150, 45)
button_rules = pygame.Rect(325, 240, 150, 45)
button_options = pygame.Rect(325, 300, 150, 45)
back_button = pygame.Rect(20, HEIGHT - 60, 100, 40)

# --- Options UI Elemanları ---
sound_button = pygame.Rect(WIDTH // 2 - 25, 230, 50, 50)
volume_slider = pygame.Rect(WIDTH // 2 - 75, 300, 150, 10)
slider_handle = pygame.Rect(volume_slider.x + 75, volume_slider.y - 5, 10, 20)
exit_button = pygame.Rect(WIDTH // 2 + 80, 300, 50, 50)

dragging_slider = False

def draw_transparent_button(rect, text, bg_color, text_color=(255, 255, 255), border_radius=10):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*bg_color[:3], 128))  # yarı saydam
    WIN.blit(s, rect.topleft)
    pygame.draw.rect(WIN, text_color, rect, 2, border_radius)
    label = FONT_BUTTON.render(text, True, text_color)
    WIN.blit(label, (
        rect.x + (rect.width - label.get_width()) // 2,
        rect.y + (rect.height - label.get_height()) // 2
    ))

def save_username(username):
    filename = "users.json"
    data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    data.append({"username": username})
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Ana Döngü ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_options:
                if sound_button.collidepoint(event.pos):
                    music_muted = not music_muted
                    if music_muted:
                        pygame.mixer.music.pause()
                        music_paused = True
                    else:
                        pygame.mixer.music.unpause()
                        music_paused = False

                elif slider_handle.collidepoint(event.pos):
                    dragging_slider = True

                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

                elif back_button.collidepoint(event.pos):
                    show_options = False
            elif show_rules:
                if back_button.collidepoint(event.pos):
                    show_rules = False
            else:
                if input_box.collidepoint(event.pos):
                    active = True
                    input_color = COLOR_ACTIVE
                else:
                    active = False
                    input_color = COLOR_INACTIVE

                if button_rules.collidepoint(event.pos):
                    show_rules = True
                elif button_options.collidepoint(event.pos):
                    show_options = True
                # Eğer butona tıklanmışsa ve username boş değilse:
                elif button_play.collidepoint(event.pos) and username.strip():
                    save_username(username.strip())

                    # Dinamik yolları oluştur
                    python_path = sys.executable  # Şu an çalışan Python yorumlayıcısının yolu
                    base_dir = os.path.dirname(os.path.abspath(__file__))  # Bu script'in bulunduğu dizin
                    client_path = os.path.join(base_dir, "client.py")  # client.py'nin tam yolu

                    # Yeni terminalde client.py'yi başlat
                    subprocess.Popen([
                    python_path,
                    client_path,
                    username
                    ], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    running = False

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False

        elif event.type == pygame.MOUSEMOTION and dragging_slider:
            x = max(volume_slider.x, min(event.pos[0], volume_slider.right - slider_handle.width))
            slider_handle.x = x
            # Ses yüksekliğini güncelle
            relative_pos = (slider_handle.centerx - volume_slider.x) / volume_slider.width
            pygame.mixer.music.set_volume(relative_pos)

        elif event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            elif event.key != pygame.K_RETURN:
                username += event.unicode

    # --- Arka plan animasyonu ---
    WIN.blit(bg_frames[current_frame], (0, 0))
    frame_counter += 1
    if frame_counter >= frame_delay_ticks:
        current_frame = (current_frame + 1) % len(bg_frames)
        frame_counter = 0

    # --- Logo ---
    if LOGO:
        WIN.blit(LOGO, (WIDTH // 2 - 50, 30))

    if not show_rules and not show_options:
        title = FONT_TITLE.render("START GAME", True, COLOR_TEXT)
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 160))

        draw_transparent_button(button_rules, "RULES", (169, 169, 169))
        draw_transparent_button(button_options, "OPTIONS", (169, 169, 169))

        input_surface = pygame.Surface((input_box.width, input_box.height), pygame.SRCALPHA)
        input_surface.fill((169, 169, 169, 128))
        WIN.blit(input_surface, (input_box.x, input_box.y))
        pygame.draw.rect(WIN, input_color, input_box, 2, border_radius=8)

        prompt = FONT_SUB.render("Enter your name:", True, COLOR_TEXT)
        WIN.blit(prompt, (input_box.x, input_box.y - 30))

        text_surface = FONT_INPUT.render(username, True, COLOR_TEXT)
        WIN.blit(text_surface, (input_box.x + 5, input_box.y + 8))
        input_box.w = max(200, text_surface.get_width() + 10)

        draw_transparent_button(button_play, "PLAY", (0, 255, 0), text_color=(0, 0, 0), border_radius=12)

    elif show_rules:
        draw_transparent_button(back_button, "BACK", (169, 169, 169))
        rules_title = FONT_TITLE.render("GAME RULES", True, COLOR_TEXT)
        WIN.blit(rules_title, (WIDTH // 2 - rules_title.get_width() // 2, 180))

        rules_lines = [
            "1. The game includes 2 cops and 1 thief.",
            "2. The thief must escape from the cops within the given time.",
            "3. Cops must catch the thief before time runs out.",
            "4. The map contains various boosts that both sides can use.",
            "5. If the thief escapes in time, the thief wins.",
            "6. If the cops catch the thief, the cops win the game."
        ]
        for i, line in enumerate(rules_lines):
            rule_text = FONT_SUB.render(line, True, COLOR_TEXT)
            WIN.blit(rule_text, (WIDTH // 2 - rule_text.get_width() // 2, 240 + i * 30))

    elif show_options:
        draw_transparent_button(back_button, "BACK", (169, 169, 169))
        options_title = FONT_TITLE.render("OPTIONS", True, COLOR_TEXT)
        WIN.blit(options_title, (WIDTH // 2 - options_title.get_width() // 2, 180))

        current_y = 250  # başlangıç yüksekliği
        spacing = 60

        # Ses Ayarları yazısı
        sound_label = FONT_SUB.render("Sound Settings", True, COLOR_TEXT)
        sound_label_x = (WIDTH // 2 - sound_label.get_width() // 2) - 40  # 40 piksel sola kaydırma
        WIN.blit(sound_label, (sound_label_x, current_y))
        current_y += spacing

        # Ses ikonu
        sound_icon_pos = (WIDTH // 2 - 25, current_y - 10)  # 3 piksel yukarı kaydırıldı
        if music_muted and SOUND_OFF_IMG:
            WIN.blit(SOUND_OFF_IMG, sound_icon_pos)
        elif not music_muted and SOUND_ON_IMG:
            WIN.blit(SOUND_ON_IMG, sound_icon_pos)
        sound_button.topleft = sound_icon_pos
        current_y += spacing

        # Ses sürgüsü
        volume_slider.center = (WIDTH // 2, current_y + 5)
        slider_handle.y = volume_slider.y - 5
        pygame.draw.rect(WIN, (180, 180, 180), volume_slider)
        pygame.draw.rect(WIN, (255, 255, 255), slider_handle)
        current_y += spacing

        # Exit butonu
        exit_button.center = (WIDTH // 2, current_y + 20)
        if EXIT_IMG:
            WIN.blit(EXIT_IMG, exit_button.topleft)
        current_y += spacing + 10

        # Küçük font
        smaller_font = pygame.font.Font(None, 17)

        # Alt bilgi yazıları
        copyright_text_1 = smaller_font.render("© 2025 Pygame.", True, COLOR_TEXT)
        copyright_text_2 = smaller_font.render("All rights reserved.", True, COLOR_TEXT)

        offset = 10  # 0.25 cm sola kaydırma

        WIN.blit(copyright_text_1, (WIDTH // 2 - copyright_text_1.get_width() // 2 - offset, HEIGHT - 50))
        WIN.blit(copyright_text_2, (WIDTH // 2 - copyright_text_2.get_width() // 2 - offset, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
