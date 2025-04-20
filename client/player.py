import pygame

class Player:
    WIDTH = 20
    HEIGHT = 20

    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role
        self.color = (0, 0, 255) if role == "polis" else (255, 0, 0)
        self.speed = 3 if role == "polis" else 2

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.WIDTH, self.HEIGHT))

    def get_data(self):
        return {"x": self.x, "y": self.y, "role": self.role}

    def update_data(self, data):
        self.x = data["x"]
        self.y = data["y"]
