import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 640, 480
BACKGROUND_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BACKGROUND_COLOR)

    pygame.display.flip()

    pygame.time.Clock().tick(60)