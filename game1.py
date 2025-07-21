import pygame
import random

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Load sounds

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Falling Object")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player setup
player_width, player_height = 50, 10
player_x = WIDTH // 2
player_y = HEIGHT - player_height - 10
player_speed = 5

# Falling object
obj_width, obj_height = 20, 20
obj_x = random.randint(0, WIDTH - obj_width)
obj_y = 0
obj_speed = 5

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)
    screen.fill(WHITE)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Move object
    obj_y += obj_speed

    # Collision detection
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    obj_rect = pygame.Rect(obj_x, obj_y, obj_width, obj_height)

    if player_rect.colliderect(obj_rect):
        score += 1
       
        obj_x = random.randint(0, WIDTH - obj_width)
        obj_y = 0
    elif obj_y > HEIGHT:
       
        obj_x = random.randint(0, WIDTH - obj_width)
        obj_y = 0

    # Draw everything
    pygame.draw.rect(screen, BLUE, player_rect)
    pygame.draw.rect(screen, RED, obj_rect)

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()