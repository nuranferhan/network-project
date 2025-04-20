# Oyuncunun oyun mantığı ve çizimi (Pygame arayüzü)
import pygame
from client.player import Player

class Game:
    def __init__(self, player_id, network):
        self.network = network
        self.player_id = player_id
        self.players = [None, None, None]
        self.init_players()

    def init_players(self):
        roles = ["polis", "polis", "hirsiz"]
        start_positions = [(100, 100), (200, 100), (150, 300)]
        for i in range(3):
            self.players[i] = Player(start_positions[i][0], start_positions[i][1], roles[i])

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.players[self.player_id].move(keys)

    def update(self):
        send_data = self.players[self.player_id].get_data()
        all_data = self.network.send(send_data)
        if all_data:
            for i, data in enumerate(all_data):
                if i != self.player_id:
                    self.players[i].update_data(data)

    def draw(self, win):
        win.fill((30, 30, 30))
        for player in self.players:
            player.draw(win)
