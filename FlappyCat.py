import sys
import pygame # type: ignore
import random
import os  # For handling file paths

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module for sound

BASE_EM = 16  # 1em is 16 pixels

# Use a temporary directory path if the script is packaged with PyInstaller
BASE_DIR = r'C:\Users\giorgos sani\Desktop\cat simulator\assets'

# Load the meow sound effect
meow_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "Meow Sound Effect.wav"))
game_over_music = os.path.join(BASE_DIR, "I Go Meow.mp3")
start_music = os.path.join(BASE_DIR, "I Go Meow.mp3")
jump_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "jump.wav"))  # Load jump sound
slap_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "slap.mp3"))


# Set up start screen variables
game_started = False
game_active = False

# Screen dimensions for 1080p
# Initialize screen size using em
SCREEN_WIDTH = int(120 * BASE_EM)  # equivalent to 1920 pixels
SCREEN_HEIGHT = int(67.5 * BASE_EM)  # equivalent to 1080 pixels
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Cat')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)  # Define light blue color for the pipes

# Game variables
gravity = 0.8
cat_movement = 0    
pipe_gap = int(18.75 * BASE_EM)  # equivalent to 300 pixels
pipe_width = int(6.25 * BASE_EM)  # equivalent to 100 pixels
pipe_speed = 5
food_spawn_probability = 0.1  # 10% chance to spawn food with each pipe pair
last_pipe_spawn_time = 0  # Track the time of the last pipe spawn
pipe_spawn_interval = 10000000  # Minimum interval between pipe spawns (in milliseconds)



cat = pygame.image.load(os.path.join(BASE_DIR, 'cat1.png'))
cat = pygame.transform.scale(cat, (98, 98))


cat_rect = cat.get_rect(center=(100, SCREEN_HEIGHT / 2))

# Load and resize background image
background = pygame.image.load(os.path.join(BASE_DIR, 'street.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load food image and set initial position
food_image = pygame.image.load(os.path.join(BASE_DIR, 'food.png'))
food_image = pygame.transform.scale(food_image, (50, 50))  # Adjust size to fit in pipes

# Pipe function to generate pipes with optional food
def create_pipe_with_food():
    pipe_height = random.randint(400, SCREEN_HEIGHT - 200)
    bottom_pipe = pygame.Rect(SCREEN_WIDTH, pipe_height, pipe_width, SCREEN_HEIGHT - pipe_height)
    top_pipe = pygame.Rect(SCREEN_WIDTH, pipe_height - pipe_gap - SCREEN_HEIGHT, pipe_width, SCREEN_HEIGHT)
    
    # Randomly decide if food should spawn with this pipe pair
    if random.random() < food_spawn_probability:
        food_position = (SCREEN_WIDTH, pipe_height - pipe_gap // 2)  # Place food in the middle of the gap
        food_rect = food_image.get_rect(center=food_position)
    else:
        food_rect = None  # No food with this pipe pair
    
    return [bottom_pipe, top_pipe], food_rect, False  # Add False as initial scored flag

# Move pipes and food to the left
def move_pipes_and_food(pipes_with_food):
    for pipes, food, scored in pipes_with_food:
        pipes[0].centerx -= pipe_speed  # Bottom pipe
        pipes[1].centerx -= pipe_speed  # Top pipe
        if food:
            food.centerx -= pipe_speed  # Move food only if it exists
    return [(pipes, food, scored) for pipes, food, scored in pipes_with_food if pipes[0].right > 0]


# Draw pipes with light blue color and add shadow for more realism
def draw_pipes_and_food(pipes_with_food):
    pipe_cap_height = 20  # Height of the pipe cap

    for pipes, food, scored in pipes_with_food:
        # Adding shadows for a more 3D look
        shadow_offset = 5  # Offset for shadow
        shadow_color = (100, 149, 237)  # Slightly darker shade of blue for shadow

        # Draw bottom pipe shadow
        shadow_rect = pipes[0].copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=15)

        # Draw top pipe shadow
        shadow_rect = pipes[1].copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=15)

        # Draw bottom pipe with light blue color
        pygame.draw.rect(screen, LIGHT_BLUE, pipes[0], border_radius=15)
        pygame.draw.rect(screen, BLACK, pipes[0], 2, border_radius=15)  # Optional outline for definition

        # Draw bottom pipe cap for a hole-like appearance
        bottom_pipe_cap = pygame.Rect(pipes[0].left - 5, pipes[0].top - pipe_cap_height, pipe_width + 10, pipe_cap_height)
        pygame.draw.rect(screen, LIGHT_BLUE, bottom_pipe_cap, border_radius=10)
        pygame.draw.rect(screen, BLACK, bottom_pipe_cap, 2, border_radius=10)  # Optional outline for definition

        # Draw top pipe with light blue color
        pygame.draw.rect(screen, LIGHT_BLUE, pipes[1], border_radius=15)
        pygame.draw.rect(screen, BLACK, pipes[1], 2, border_radius=15)  # Optional outline for definition

        # Draw top pipe cap for a hole-like appearance
        top_pipe_cap = pygame.Rect(pipes[1].left - 5, pipes[1].bottom, pipe_width + 10, pipe_cap_height)
        pygame.draw.rect(screen, LIGHT_BLUE, top_pipe_cap, border_radius=10)
        pygame.draw.rect(screen, BLACK, top_pipe_cap, 2, border_radius=10)  # Optional outline for definition

        # Draw food if it exists
        if food:
            screen.blit(food_image, food)
            
# Check for collisions with pipes
def check_collision(pipes_with_food):
    for pipes, food, scored in pipes_with_food:
        if cat_rect.colliderect(pipes[0]) or cat_rect.colliderect(pipes[1]):
            slap_sound.play()  # Play slap sound when a crash happens
            return False
    if cat_rect.top <= 0 or cat_rect.bottom >= SCREEN_HEIGHT:
        slap_sound.play()  # Play slap sound if the cat hits the top or bottom of the screen
        return False
    return True

def check_food_collision(food_rect):
    if food_rect and cat_rect.colliderect(food_rect):
        meow_sound.play()  # Play meow sound when cat collects food
        return True
    return False

# Score display function
def display_score(score):
    font = pygame.font.Font(None, 72)  # Increased font size for larger screen
    text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(text, (50, 50))

# Game loop variables
clock = pygame.time.Clock()
pipes_with_food = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

score = 0
game_active = True

pygame.mixer.music.load(start_music)
pygame.mixer.music.play(-1)  # Loop until the game starts

# Main game loop
while True:
    current_time = pygame.time.get_ticks()  # Get current time in milliseconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check for click or space to start the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started:  # Only for the initial start screen
                game_started = True
                game_active = True
                pygame.mixer.music.stop()  # Stop the start screen music
            elif game_active:
                cat_movement = 0
                cat_movement -= 12  # Jump with space bar
                jump_sound.play()  # Play jump sound
            elif  not game_active:
                game_active = True
                pipes_with_food.clear()
                cat_rect.center = (100, SCREEN_HEIGHT / 2)
                cat_movement = 0
                score = 0
                pygame.mixer.music.stop()  # Stop game-over music

        if event.type == SPAWNPIPE and game_active:
            # Create a new pipe pair with optional food
            pipes_with_food.append(create_pipe_with_food())

    screen.blit(background, (0, 0))

    if not game_started:
        # Display start message
        font = pygame.font.Font(None, 72)
        text = font.render("Click or Tap Space to Start...", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

    elif game_active:
        # Cat movement
        cat_movement += gravity
        cat_rect.centery += cat_movement
        screen.blit(cat, cat_rect)

        # Spawn new pipe pair if enough time has passed since the last spawn
        if current_time - last_pipe_spawn_time > pipe_spawn_interval:
            pipes_with_food.append(create_pipe_with_food())
            last_pipe_spawn_time = current_time  # Update the last spawn time
            
        # Move pipes and food
        pipes_with_food = move_pipes_and_food(pipes_with_food)
        draw_pipes_and_food(pipes_with_food)

        # Collision check with pipes
        game_active = check_collision(pipes_with_food)

        # Check if the cat collects any food
        for i, (pipes, food, scored) in enumerate(pipes_with_food):
            if food and check_food_collision(food):
                score += 5  # Increase score by 5 for collecting food
                pipes_with_food[i] = (pipes, None, scored)  # Remove only the food

            # Score update for passing pipes without food, only if not already scored
            if pipes[0].centerx < cat_rect.centerx and not scored:
                score += 1  # Increase score by 1 for passing pipes without food
                pipes_with_food[i] = (pipes, food, True)  # Mark as scored

        # Display score
        display_score(score)

    elif not game_active:
        
        # Start game-over music if it's not already playing
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(game_over_music)
            pygame.mixer.music.play(-1)  # Loop the game over music

        # Display game over message
        font = pygame.font.Font(None, 96)  # Increased font size for larger screen
        text = font.render("Game Over!", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Display the score below the game over message
        font = pygame.font.Font(None, 72)  # Adjust font size for score
        score_text = font.render(f'Score: {score}', True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))  # Adjust y position for spacing
        screen.blit(score_text, score_rect)

    pygame.display.update()
    clock.tick(60) 