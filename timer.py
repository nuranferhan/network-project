import pygame
from gameconfig import *

pygame.font.init()

class Timer:
    def __init__(self, total_time_seconds=180):
        self.total_time = total_time_seconds
        self.started = False
        self.start_ticks = 0

    def start(self):
        self.start_ticks = pygame.time.get_ticks()
        self.started = True

    def stop(self):
        self.started = False

    def is_running(self):
        return self.started and self.get_time_left() > 0

    def get_time_left(self):
        if not self.started:
            return self.total_time
        elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        return max(self.total_time - elapsed_seconds, 0)

    def draw(self, surface, width):
        time_left = self.get_time_left()
        minutes = time_left // 60
        seconds = time_left % 60
        time_str = f"Time Left: {minutes:02}:{seconds:02}"
        render = TIMER_FONT.render(time_str, True, (255, 255, 255))
        surface.blit(render, (width - render.get_width() - 10, 10))

    """eklendi: homescreeen ekranından client ekranına bağlanma sonrası timer hatası için ;17.05.2025"""
    def is_finished(self):  # ✅ EKLENEN METOD
        return self.get_time_left() == 0
