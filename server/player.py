# Oyuncu state'leri burada da tutulur
class Player:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role
        self.speed = 3 if role == "polis" else 2

    def update(self, data):
        self.x = data["x"]
        self.y = data["y"]

    def get_data(self):
        return {"x": self.x, "y": self.y, "role": self.role}
