import pygame
from client.network import Network
from client.game import Game

WIN_WIDTH = 600
WIN_HEIGHT = 400

def run_client():
    pygame.init()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Hırsız-Polis Online")

    network = Network()
    player_id = network.player_id  # Burada sunucudan ID alındı zaten
    game = Game(player_id, network)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        game.handle_keys()
        game.update()
        game.draw(win)
        pygame.display.update()

    pygame.quit()
