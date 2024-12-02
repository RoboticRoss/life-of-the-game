import pygame
import numpy as np
import random

# Initialize pygame and sound
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 1000
CELL_SIZE = 10
FPS = 10


REPRODUCTION = 3
OVERPOPULATION = 4
UNDERPOPULATION = 2

# Basically interprets REPRODUCTION + .5 if true; RANDOM OCCURANCE LESS PATTERNS
POINTFIVE = False

TRAGEDY = False


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_COLOR = (30, 30, 50)

# Sound Constants
BASE_FREQUENCY = 110  # Base frequency for tones (in Hz)
FREQUENCY_STEP = 4   # Frequency step per cell change
DURATION = 100        # Duration of each tone (in milliseconds)

# Calculate grid dimensions
cols = WIDTH // CELL_SIZE
rows = HEIGHT // CELL_SIZE

# Initialize grid
grid = np.zeros((rows, cols), dtype=int)
transitions = np.zeros((rows, cols), dtype=float)  # Track transition brightness

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()

def generate_tone(frequency, duration, sample_rate=44100):
    """Generates a tone of a given frequency and duration."""
    t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), endpoint=False)
    wave = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)  # Generate sine wave

    wave = np.column_stack((wave, wave))  # Duplicate wave for both left and right channels

    return pygame.sndarray.make_sound(wave)

def play_tone(changes):
    """Plays a tone based on the number of changes."""
    if changes > 0:
        frequency = BASE_FREQUENCY + changes * FREQUENCY_STEP
        tone = generate_tone(frequency, DURATION)
        tone.play()


def draw_grid():
    """Draws the grid lines."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


def draw_cells():
    """Draws the live cells with smooth transitions."""
    for row in range(rows):
        for col in range(cols):
            brightness = transitions[row, col]
            color = (int(WHITE[0] * brightness), int(WHITE[1] * brightness), int(WHITE[2] * brightness))
            if brightness > 0:  # Draw only if visible
                pygame.draw.rect(
                    screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )



def update_grid():
    """Applies Conway's rules to update the grid and manage transitions."""
    global grid, transitions
    new_grid = np.copy(grid)
    changes = 0
    for row in range(rows):
        for col in range(cols):
            # Count live neighbors
            neighbors = (
                grid[row - 1, col - 1]
                + grid[row - 1, col]
                + grid[row - 1, (col + 1) % cols]
                + grid[row, col - 1]
                + grid[row, (col + 1) % cols]
                + grid[(row + 1) % rows, col - 1]
                + grid[(row + 1) % rows, col]
                + grid[(row + 1) % rows, (col + 1) % cols]
            )

            # Apply rules
            if grid[row, col] == 1:
                if neighbors < UNDERPOPULATION or neighbors > OVERPOPULATION:  # Underpopulation or overpopulation
                    new_grid[row, col] = 0
                    changes += 1
                elif TRAGEDY and random.randint(1,10) == 1:
                    print("OH NO")
                    new_grid[row, col] = 0
                    changes += 1
            else:
                if neighbors == REPRODUCTION:  # Reproduction
                    new_grid[row, col] = 1
                    changes += 1
                elif neighbors == REPRODUCTION - 1 and POINTFIVE and random.choice([True, False, False, False]):
                    print("AYY")
                    new_grid[row, col] = 1
                    changes += 1

            # Manage transitions
            if new_grid[row, col] == 1:
                transitions[row, col] = min(transitions[row, col] + 1.0, 1.0)  # Fade in
            else:
                transitions[row, col] = max(transitions[row, col] - 0.5, 0.0)  # Fade out

    grid = new_grid
    play_tone(changes)  # Play tone based on number of changes


def handle_input():
    """Handles mouse input to toggle cells."""
    mouse_pos = pygame.mouse.get_pos()
    x, y = mouse_pos[0] // CELL_SIZE, mouse_pos[1] // CELL_SIZE
    grid[y, x] = 1 - grid[y, x]  # Toggle cell state
    transitions[y, x] = 1 if grid[y, x] == 1 else 0  # Immediate update for clicked cell


# Game loop
running = True
paused = True

while running:
    screen.fill(BLACK)
    draw_grid()
    draw_cells()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and paused:
            handle_input()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:  # Reset the grid
                grid = np.zeros((rows, cols), dtype=int)
                transitions = np.zeros((rows, cols), dtype=float)

    if not paused:
        update_grid()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
