import os
from scoreboard import Scoreboard
from gameconfig import *

# Font sistemini başlat
pygame.font.init()

def load_gamebar_texture(width, height):
    frames = []
    frame_dir = os.path.join("assets", "gamebar_texture")

    # Load all frames (31 frames total)
    for i in range(31):
        frame_path = os.path.join(frame_dir, f"frame_{i:02d}_delay-0.02s.gif")
        try:
            frame = pygame.image.load(frame_path).convert_alpha()
            frames.append(pygame.transform.scale(frame, (width, height)))
        except pygame.error:
            print(f"Warning: Could not load frame: {frame_path}")

    # Use the current time to determine which frame to show (each frame shows for 0.02s)
    current_time = pygame.time.get_ticks()
    frame_index = (current_time // 60) % len(frames)

    return frames[frame_index]


# Oyun alanı arka planını yükle ve ölçekle
def load_background_texture(width, height):
    path = os.path.join("assets", "old.png")
    texture = pygame.image.load(path).convert()
    return pygame.transform.scale(texture, (width, height))


def redraw_window(surface, player1, other_players, walls, width, height, message=None,
                  scoreboard=None, timer=None, boost_manager=None, fog_bool=False,
                  high_score=0, high_score_username="", final_scores_data=None,
                  background_img=None):
    # Ana yüzeyi temizle
    surface.fill(BLACK)

    # 1. Game bar çiz
    gamebar_surface = load_gamebar_texture(width, GAMEBAR_HEIGHT)
    surface.blit(gamebar_surface, (0, 0))

    # 2. Oyun alanının arka planını çiz (game bar'ın altından başlar)
    # Eğer background_img parametresi verilmemişse, map.png'yi yükle
    if background_img is None:
        background_img = load_background_texture(width, height - GAMEBAR_HEIGHT)

    # Arka planı çiz
    surface.blit(background_img, (0, GAMEBAR_HEIGHT))

    # Timer'ı çiz (oyun bitmediyse)
    game_over_messages = [
        'YOU GOT CAUGHT!!!',
        'You Escaped Successfully!',
        'YOU CAUGHT THE GUY!!!',
        'The guy got away!'
    ]
    if timer is not None and message not in game_over_messages:
        timer_text = TIMER_FONT.render(f"Time: {int(timer)}", 1, WHITE)
        surface.blit(timer_text, (width - timer_text.get_width() - 10,
                                  (GAMEBAR_HEIGHT - timer_text.get_height()) // 2))

    # Yüksek skoru ortada göster
    if high_score is not None and high_score_username:
        high_score_text = HIGH_SCORE_FONT.render(f"High Score: {high_score}", 1, WHITE)
        surface.blit(high_score_text, (width / 2 - high_score_text.get_width() / 2,
                                       (GAMEBAR_HEIGHT - high_score_text.get_height()) // 2))
    elif high_score is not None:
        high_score_text = HIGH_SCORE_FONT.render(f"High Score: {high_score}", 1, WHITE)
        surface.blit(high_score_text, (width / 2 - high_score_text.get_width() / 2,
                                       (GAMEBAR_HEIGHT - high_score_text.get_height()) // 2))

    # 3. Duvarları çiz
    for wall in walls:
        pygame.draw.rect(surface, WALL_COLOR, wall)

    # 4. Boost manager varsa boostları çiz
    if boost_manager:
        boost_manager.draw(surface)

    # 5. Oyuncuları çiz
    if player1:
        player1.draw(surface)

    if other_players:
        for p in other_players:
            p.draw(surface)

    # 7. Skor tablosunu çiz
    if scoreboard:
        scoreboard.draw(surface)

    # 9. Sis efekti
    if player1 and fog_bool:
        fog = pygame.Surface((width, height - GAMEBAR_HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))
        center_x = int(player1.x + player1.width / 2)
        center_y = int(player1.y + player1.height / 2 - GAMEBAR_HEIGHT)
        pygame.draw.circle(fog, (0, 0, 0, 0), (center_x, center_y), RADIUS)
        surface.blit(fog, (0, GAMEBAR_HEIGHT))

    # 8. Mesaj veya final skor tablosu
    if final_scores_data is not None:
        Scoreboard.draw_final_scoreboard(surface, final_scores_data, timer,width, height)
        pygame.display.update()
        return  # Scoreboard gösterildiyse diğer şeyleri çizme
    elif message:
        lines = message.split('\n')
        total_message_height = len(lines) * MSG_FONT.get_linesize()
        y_offset = height / 2 - total_message_height / 2

        for line in lines:
            text_surface = MSG_FONT.render(line, 1, WHITE)
            text_x = width / 2 - text_surface.get_width() / 2
            surface.blit(text_surface, (text_x, y_offset))
            y_offset += MSG_FONT.get_linesize()

    pygame.display.update()