import pygame
from gameconfig import *

# Pygame font sistemini başlat
pygame.font.init()

class Scoreboard:
    """
    Oyuncunun skorunu ve rolünü takip eder ve ekrana çizer.
    Ayrıca oyun sonu skor tablosunu çizmek için statik bir metod içerir.
    """
    def __init__(self, username, role, score=0):
        self.username = username
        self.role = role
        self.score = score
        self.score_changed = False # Skorun değişip değişmediğini takip etmek için

    def update_score(self, new_score):
        """Skoru günceller ve skorun değişip değişmediğini işaretler."""
        if self.score != new_score:
            self.score_changed = True
        self.score = new_score
        return self.score_changed

    def add_points(self, points):
        """Skora puan ekler ve skorun değiştiğini işaretler."""
        self.score += points
        self.score_changed = True
        return self.score

    def reset_changed_flag(self):
        """Skor değişim bayrağını sıfırlar."""
        self.score_changed = False

    def draw(self, surface):
        """Mevcut oyuncunun skorunu oyun çubuğuna çizer."""
        text = f"{self.username} ({self.role}): {self.score}"
        render = SCORE_FONT.render(text, True, (255, 255, 255))
        # Oyun çubuğunda sol üst köşeye yakın çizer
        surface.blit(render, (10, (50 - render.get_height()) // 2))  # 50 = gamebar_height

    @staticmethod
    def draw_final_scoreboard(surface, players_data, timer,screen_width, screen_height):
        """
        Oyun bittiğinde nihai skor tablosunu ekrana çizer.

        Args:
            surface (pygame.Surface): Çizim yapılacak yüzey.
            players_data (dict): Oyuncu verilerini içeren bir sözlük.
                                 Beklenen format: {oyuncu_id: {'username': str, 'role': str, 'score': int}}
            screen_width (int): Oyun penceresinin genişliği.
            screen_height (int): Oyun penceresinin yüksekliği.
        """
        # Skor tablosu dikdörtgeninin boyutları ve konumu (ekranın ortasında)
        board_width = screen_width * 0.5
        board_height = screen_height * 0.5
        board_x = (screen_width - board_width) // 2
        board_y = (screen_height - board_height) // 2

        # Yarı saydam arka plan yüzeyi oluştur
        board_surface = pygame.Surface((board_width, board_height), pygame.SRCALPHA)
        # Siyah renk, 180 alfa değeri (yarı saydam)
        board_surface.fill((0, 0, 0, 180))
        surface.blit(board_surface, (board_x, board_y))

        # Beyaz kenarlık çiz
        pygame.draw.rect(surface, (255, 255, 255), (board_x, board_y, board_width, board_height), 3)

        # Başlık çiz
        title_render = SCOREBOARD_TITLE_FONT.render("Final Scores", True, (255, 255, 255))
        title_x = board_x + (board_width - title_render.get_width()) // 2
        title_y = board_y + 20
        surface.blit(title_render, (title_x, title_y))

        # Oyuncu skorlarını listele
        line_height = SCOREBOARD_SCORE_FONT.get_linesize()
        start_y = title_y + title_render.get_height() + 20 # Başlığın altından başla

        # Oyuncuları skora göre sırala (isteğe bağlı, ancak daha düzenli görünür)
        # players_data bir sözlük olduğu için .values() ile değerleri alıp listeye çeviriyoruz
        # key=lambda item: item['score'] ile 'score' anahtarına göre sıralıyoruz
        # reverse=True ile yüksekten düşüğe sıralıyoruz

        """eklendi: Hem dict hem list ile çalışabilecek şekilde kontrol et; 17.05.2025"""
        if isinstance(players_data, list):
            sorted_players = sorted(players_data, key=lambda item: item.get('score', 0), reverse=True)
        else:
            sorted_players = sorted(players_data.values(), key=lambda item: item.get('score', 0), reverse=True)

        for i, player_data in enumerate(sorted_players):
            # Her oyuncunun skor bilgisini formatla
            # .get() kullanarak anahtarın varlığını kontrol et, yoksa varsayılan değer kullan
            username = player_data.get('username', 'Bilinmeyen Oyuncu')
            role = player_data.get('role', 'rol yok')
            score = player_data.get('score', 0)

            text = f"{username} ({role.capitalize()}): {score}"
            score_render = SCOREBOARD_SCORE_FONT.render(text, True, (255, 255, 255))

            # Skor metnini yatay olarak ortala (başlık gibi)
            score_x = board_x + (board_width - score_render.get_width()) // 2
            # Yazıları aşağıya taşımak için ek bir piksel değeri ekliyoruz
            additional_offset = 40
            score_y = start_y + i * line_height + additional_offset

            surface.blit(score_render, (score_x, score_y))

        # Timer'ı skorların altına yerleştiriyoruz
        timer_text = TIMER_FONT.render(f"Time: {int(timer)}", 1, WHITE)
        timer_y = score_y + line_height + 10  # Skorların altına biraz boşluk bırakarak
        timer_x = score_x + 38  # 1 cm sağa kaydır
        surface.blit(timer_text, (timer_x, timer_y))