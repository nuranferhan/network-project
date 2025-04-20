from server.player import Player

class Game:
    def __init__(self):
        self.players = []
        self.init_players()

    def init_players(self):
        roles = ["polis", "polis", "hirsiz"]
        start_positions = [(100, 100), (200, 100), (150, 300)]
        for i in range(3):
            p = Player(start_positions[i][0], start_positions[i][1], roles[i])
            self.players.append(p)

    def update_player(self, player_id, data):
        self.players[player_id].update(data)

    def get_all_data(self):
        return [p.get_data() for p in self.players] 
