import pygame
import random
import sys
import math
import array
import asyncio

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

def note_to_freq(note):
    """Convert MIDI note number to frequency in Hz."""
    return 440 * (2 ** ((note - 69) / 12))

def create_tone(frequency, duration, sample_rate=22050):
    """Generate a tone at the given frequency using pure Python."""
    num_samples = int(duration * sample_rate)
    # Create a sound buffer
    buf = array.array('h')  # 16-bit signed integers

    max_amplitude = 32767 * 0.3  # 30% volume

    for i in range(num_samples):
        t = i / sample_rate
        # Create sine wave
        value = math.sin(2 * math.pi * frequency * t)
        # Add envelope to prevent clicking
        envelope = math.exp(-3 * t / duration)
        # Convert to 16-bit PCM
        sample = int(value * envelope * max_amplitude)
        # Stereo: add same sample twice
        buf.append(sample)
        buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)

def create_happy_song():
    """Creates a cheerful song for gameplay."""
    # Happy upbeat melody (C major scale)
    # MIDI notes: C, E, G, E, F, A, G, E, D, F, E, C
    notes = [60, 64, 67, 64, 65, 69, 67, 64, 62, 65, 64, 60]
    sounds = []

    for note in notes:
        freq = note_to_freq(note)
        sound = create_tone(freq, 0.25)
        sounds.append(sound)

    return sounds

def create_sad_song():
    """Creates a sad 'whomp whomp whomp' song for game over."""
    # Three descending sad tones
    notes = [48, 45, 42]
    sounds = []

    for note in notes:
        freq = note_to_freq(note)
        sound = create_tone(freq, 0.8)
        sounds.append(sound)

    return sounds

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario vs Mad Goombas")
clock = pygame.time.Clock()

# Create music
happy_sounds = create_happy_song()
sad_sounds = create_sad_song()
current_happy_note = 0
music_timer = 0

def draw_block_letters():
    """Draws GAME OVER in block letters."""
    # Block letter patterns (5x5 grid for each letter)
    letters = {
        'G': [
            " ### ",
            "#    ",
            "# ## ",
            "#  # ",
            " ### "
        ],
        'A': [
            " ### ",
            "#   #",
            "#####",
            "#   #",
            "#   #"
        ],
        'M': [
            "#   #",
            "## ##",
            "# # #",
            "#   #",
            "#   #"
        ],
        'E': [
            "#####",
            "#    ",
            "#### ",
            "#    ",
            "#####"
        ],
        'O': [
            " ### ",
            "#   #",
            "#   #",
            "#   #",
            " ### "
        ],
        'V': [
            "#   #",
            "#   #",
            "#   #",
            " # # ",
            "  #  "
        ],
        'R': [
            "#### ",
            "#   #",
            "#### ",
            "#  # ",
            "#   #"
        ]
    }

    block_size = 10
    start_x = 150
    start_y = 100

    # Draw "GAME"
    word = "GAME"
    for letter_index, letter in enumerate(word):
        for row_index, row in enumerate(letters[letter]):
            for col_index, char in enumerate(row):
                if char == '#':
                    x = start_x + letter_index * 60 + col_index * block_size
                    y = start_y + row_index * block_size
                    pygame.draw.rect(screen, WHITE, (x, y, block_size - 1, block_size - 1))

    # Draw "OVER"
    word = "OVER"
    start_y = 200
    for letter_index, letter in enumerate(word):
        for row_index, row in enumerate(letters[letter]):
            for col_index, char in enumerate(row):
                if char == '#':
                    x = start_x + letter_index * 60 + col_index * block_size
                    y = start_y + row_index * block_size
                    pygame.draw.rect(screen, WHITE, (x, y, block_size - 1, block_size - 1))

    # Draw restart message
    font = pygame.font.Font(None, 36)
    text = font.render("Press SPACE to restart", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 320))
    screen.blit(text, text_rect)

def reset_game():
    """Initializes or resets all game variables."""
    global player_rect, player_vel_y, is_jumping, obstacles, enemies, scroll_timer, ground_enemy_timer, game_over, current_happy_note, music_timer
    player_rect = pygame.Rect(100, 200, 32, 40)
    player_vel_y = 0
    is_jumping = False
    obstacles = []
    enemies = []
    scroll_timer = 0
    ground_enemy_timer = 0
    game_over = False
    current_happy_note = 0
    music_timer = 0

    # Clear any pending timer events for sad music
    for i in range(3):
        pygame.time.set_timer(pygame.USEREVENT + i, 0)

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

def draw_player_happy(rect):
    """Draws the player as a happy person."""
    # Body
    pygame.draw.rect(screen, MARIO_RED, rect)
    # Head (lighter skin tone)
    head_size = rect.width - 4
    pygame.draw.circle(screen, (255, 220, 177), (rect.centerx, rect.y + 12), head_size // 2)
    # Eyes
    pygame.draw.circle(screen, BLACK, (rect.centerx - 6, rect.y + 10), 2)
    pygame.draw.circle(screen, BLACK, (rect.centerx + 6, rect.y + 10), 2)
    # Happy smile (arc)
    smile_points = []
    for i in range(-6, 7, 2):
        x = rect.centerx + i
        y = rect.y + 16 + abs(i) // 3
        smile_points.append((x, y))
    if len(smile_points) > 1:
        pygame.draw.lines(screen, BLACK, False, smile_points, 2)

def draw_player_sad(rect):
    """Draws the player as a sad person."""
    # Body
    pygame.draw.rect(screen, MARIO_RED, rect)
    # Head (lighter skin tone)
    head_size = rect.width - 4
    pygame.draw.circle(screen, (255, 220, 177), (rect.centerx, rect.y + 12), head_size // 2)
    # Eyes (X's for dead/sad)
    pygame.draw.line(screen, BLACK, (rect.centerx - 8, rect.y + 8), (rect.centerx - 4, rect.y + 12), 2)
    pygame.draw.line(screen, BLACK, (rect.centerx - 4, rect.y + 8), (rect.centerx - 8, rect.y + 12), 2)
    pygame.draw.line(screen, BLACK, (rect.centerx + 4, rect.y + 8), (rect.centerx + 8, rect.y + 12), 2)
    pygame.draw.line(screen, BLACK, (rect.centerx + 8, rect.y + 8), (rect.centerx + 4, rect.y + 12), 2)
    # Frowny face
    frown_points = []
    for i in range(-6, 7, 2):
        x = rect.centerx + i
        y = rect.y + 19 - abs(i) // 3
        frown_points.append((x, y))
    if len(frown_points) > 1:
        pygame.draw.lines(screen, BLACK, False, frown_points, 2)

# Initialize the first game state
reset_game()

# --- Main Game Loop ---
async def main():
    global music_timer, current_happy_note, game_over, player_vel_y, is_jumping, ground_enemy_timer, player_rect, obstacles, enemies
    while True:
        screen.fill(SKY_BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Handle sad music timer events
            elif event.type >= pygame.USEREVENT and event.type < pygame.USEREVENT + 3:
                sound_index = event.type - pygame.USEREVENT
                if sound_index < len(sad_sounds):
                    sad_sounds[sound_index].play()

        keys = pygame.key.get_pressed()

        # Handle game over state
        if game_over:
            # Draw the game scene with sad player
            pygame.draw.rect(screen, GRASS_GREEN, (0, 350, SCREEN_WIDTH, 50)) # Ground
            for block in obstacles:
                pygame.draw.rect(screen, PLATFORM_BROWN, block)
            for enemy in enemies:
                draw_enemy(enemy)
            draw_player_sad(player_rect) # Sad player
            # Draw GAME OVER on top
            draw_block_letters()
            if keys[pygame.K_SPACE]:
                reset_game()
            pygame.display.update()
            clock.tick(FPS)
            await asyncio.sleep(0)
            continue

        # Play happy music (loop through notes)
        music_timer += 1
        if music_timer >= 15:  # Play a note every 15 frames (~0.25 seconds at 60 FPS)
            happy_sounds[current_happy_note].play()
            current_happy_note = (current_happy_note + 1) % len(happy_sounds)
            music_timer = 0

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
                    game_over = True
                    # Stop happy music and play sad music (whomp whomp whomp)
                    pygame.mixer.stop()
                    for i, sound in enumerate(sad_sounds):
                        # Play each whomp with a delay
                        pygame.time.set_timer(pygame.USEREVENT + i, i * 600)  # 600ms between whomps

        # Cleanup off-screen items
        obstacles = [b for b in obstacles if b.right > -50]
        enemies = [e for e in enemies if e.right > -50]

        # 6. Drawing
        pygame.draw.rect(screen, GRASS_GREEN, (0, 350, SCREEN_WIDTH, 50)) # Ground
        for block in obstacles:
            pygame.draw.rect(screen, PLATFORM_BROWN, block)
        for enemy in enemies:
            draw_enemy(enemy)
        draw_player_happy(player_rect) # Player

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

# Run the game
asyncio.run(main())

