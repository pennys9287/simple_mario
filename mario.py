import pygame
import random
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
MARIO_RED = (255, 0, 0)
GRASS_GREEN = (34, 139, 34)
PLATFORM_BROWN = (139, 69, 19)
GOOMBA_BROWN = (150, 75, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Physics
GRAVITY = 1
JUMP_STRENGTH = -16
SCROLL_SPEED = 6

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario vs Mad Goombas")
clock = pygame.time.Clock()

def reset_game():
    """Initializes or resets all game variables."""
    global player_rect, player_vel_y, is_jumping, obstacles, enemies, scroll_timer, ground_enemy_timer
    player_rect = pygame.Rect(100, 200, 32, 40)
    player_vel_y = 0
    is_jumping = False
    obstacles = []
    enemies = []
    scroll_timer = 0
    ground_enemy_timer = 0

    # Starting platforms
    last_x = 400
    for _ in range(5):
        new_p = pygame.Rect(last_x, random.choice([280, 220, 160]), 100, 20)
        obstacles.append(new_p)
        # 50% chance to spawn an enemy on this platform
        if random.random() > 0.5:
            enemies.append(pygame.Rect(new_p.centerx - 15, new_p.top - 30, 30, 30))
        last_x = new_p.x + 100 + random.randint(60, 150)

    # Starting ground enemies
    ground_x = 600
    for _ in range(3):
        enemies.append(pygame.Rect(ground_x, 320, 30, 30))
        ground_x += random.randint(150, 300)

def draw_enemy(rect):
    """Draws a brown square with a mad face."""
    pygame.draw.rect(screen, GOOMBA_BROWN, rect)
    # Eyes
    pygame.draw.circle(screen, WHITE, (rect.x + 8, rect.y + 10), 4)
    pygame.draw.circle(screen, WHITE, (rect.x + 22, rect.y + 10), 4)
    # Mad eyebrows (diagonal lines)
    pygame.draw.line(screen, BLACK, (rect.x + 4, rect.y + 4), (rect.x + 12, rect.y + 8), 2)
    pygame.draw.line(screen, BLACK, (rect.x + 26, rect.y + 4), (rect.x + 18, rect.y + 8), 2)
    # Frown
    pygame.draw.line(screen, BLACK, (rect.x + 10, rect.y + 24), (rect.x + 20, rect.y + 24), 2)

# Initialize the first game state
reset_game()

# --- Main Game Loop ---
while True:
    screen.fill(SKY_BLUE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()

    # 1. Auto-scrolling & Movement
    # Scroll obstacles automatically
    for block in obstacles: block.x -= SCROLL_SPEED
    # Scroll enemies automatically
    for enemy in enemies: enemy.x -= SCROLL_SPEED

    # Spawn new platforms/enemies as we move
    if obstacles[-1].x < SCREEN_WIDTH:
        new_x = obstacles[-1].x + 100 + random.randint(60, 160)
        new_p = pygame.Rect(new_x, random.choice([280, 220, 160]), 100, 20)
        obstacles.append(new_p)
        if random.random() > 0.4: # Spawn enemy on new platform
            enemies.append(pygame.Rect(new_p.centerx - 15, new_p.top - 30, 30, 30))

    # Spawn ground enemies periodically
    ground_enemy_timer += 1
    if ground_enemy_timer > random.randint(60, 120):  # Every 1-2 seconds
        enemies.append(pygame.Rect(SCREEN_WIDTH + 20, 320, 30, 30))
        ground_enemy_timer = 0

    # Player can still move left/right relative to the scrolling
    if keys[pygame.K_LEFT] and player_rect.x > 0:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT] and player_rect.x < SCREEN_WIDTH - player_rect.width:
        player_rect.x += 5

    # 2. Jump & Gravity
    if keys[pygame.K_SPACE] and not is_jumping:
        player_vel_y = JUMP_STRENGTH
        is_jumping = True

    player_vel_y += GRAVITY
    player_rect.y += player_vel_y

    # 3. Collisions: Floor
    if player_rect.bottom >= 350:
        player_rect.bottom = 350
        player_vel_y = 0
        is_jumping = False

    # 4. Collisions: Platforms
    for block in obstacles:
        if player_rect.colliderect(block):
            if player_vel_y > 0 and player_rect.bottom < block.top + 20:
                player_rect.bottom = block.top
                player_vel_y = 0
                is_jumping = False

    # 5. Collisions: Enemies
    for enemy in enemies[:]: # Use [:] to allow removing items while looping
        if player_rect.colliderect(enemy):
            # Did we jump on top? (Falling and player bottom is high enough)
            if player_vel_y > 0 and player_rect.bottom < enemy.top + 20:
                enemies.remove(enemy)
                player_vel_y = -10 # Little bounce
            else:
                # We hit the side or bottom -> Game Over
                reset_game()

    # Cleanup off-screen items
    obstacles = [b for b in obstacles if b.right > -50]
    enemies = [e for e in enemies if e.right > -50]

    # 6. Drawing
    pygame.draw.rect(screen, GRASS_GREEN, (0, 350, SCREEN_WIDTH, 50)) # Ground
    for block in obstacles:
        pygame.draw.rect(screen, PLATFORM_BROWN, block)
    for enemy in enemies:
        draw_enemy(enemy)
    pygame.draw.rect(screen, MARIO_RED, player_rect) # Player

    pygame.display.update()
    clock.tick(FPS)

