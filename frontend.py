import pygame
import subprocess
import sys
import os

# Initialize Pygame
pygame.init()

# Constants for window layout
WINDOW_WIDTH = 1800  # Width to fit 3 games side by side
WINDOW_HEIGHT = 1200  # Height to fit 2 games vertically
GAME_WIDTH = 600
GAME_HEIGHT = 600

# Create main window
main_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Games Collection')

# List of games to launch in table layout order (left to right)
games = [
    # Row 1
    "BlindSearch/AIproject1.py",
    "Search_Algorithms_Terminology/Binary_Search.py",
    "LocalSearch/AIproject3.py",
    # Row 2 
    "LookingResistance/AIproject4.py",
    "SeekingComfort/AIproject5.py"
]

# Launch all games
processes = []
for i, game_path in enumerate(games):
    try:
        # Calculate table position (left to right, top to bottom)
        row = i // 3
        col = i % 3
        x = col * GAME_WIDTH
        y = row * GAME_HEIGHT
        
        # Set environment variables for window position
        env = os.environ.copy()
        env['SDL_WINDOW_POS'] = f"{x},{y}"
        
        # Launch game process
        process = subprocess.Popen(['python', game_path], env=env)
        processes.append(process)
    except Exception as e:
        print(f"Error launching {game_path}: {e}")

# Keep window open until all games are closed
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Check if all processes have ended
    if all(process.poll() is not None for process in processes):
        running = False

# Clean up
for process in processes:
    process.terminate()
pygame.quit()
sys.exit()
