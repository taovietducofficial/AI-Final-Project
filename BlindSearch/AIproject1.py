import pygame
import random
import collections
from enum import Enum

# Define directions
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE_X = 600
WINDOW_SIZE_Y = 300
GRID_COUNT_X = 30
GRID_COUNT_Y = 15
GRID_SIZE = WINDOW_SIZE_Y // GRID_COUNT_Y

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255) 
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption('Snake Game - Blind Search')

class SnakeGame:
    def __init__(self):
        # Cache movement vectors
        self.movement_vectors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        # Pre-calculate grid positions
        self.grid_positions = set((x, y) for x in range(GRID_COUNT_X) for y in range(GRID_COUNT_Y))
        self.reset()

    def reset(self):
        # Initial snake position (middle of screen)
        self.snake = collections.deque([(GRID_COUNT_X//2, GRID_COUNT_Y//2)])
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        # Get valid positions by subtracting snake positions from all grid positions
        valid_positions = self.grid_positions - set(self.snake)
        return random.choice(tuple(valid_positions))

    def blind_search(self):
        # Optimized BFS with early exit and efficient data structures
        queue = collections.deque([(self.snake[0], [])])
        visited = {self.snake[0]}
        snake_set = set(self.snake)
        target = self.food
        
        while queue:
            pos, path = queue.popleft()
            if pos == target:
                return path[0] if path else None

            # Use cached movement vectors
            for dx, dy in self.movement_vectors:
                new_x = (pos[0] + dx) % GRID_COUNT_X
                new_y = (pos[1] + dy) % GRID_COUNT_Y
                new_pos = (new_x, new_y)
                
                if new_pos not in visited and new_pos not in snake_set:
                    visited.add(new_pos)
                    new_path = path + [new_pos]
                    queue.append((new_pos, new_path))
                    
                    # Early exit if we found food
                    if new_pos == target:
                        return new_path[0]
        return None

    def update(self):
        if self.game_over:
            return

        # Find next move using optimized blind search
        next_move = self.blind_search()
        if next_move:
            head_x, head_y = self.snake[0]
            next_x, next_y = next_move
            
            # Optimized direction determination using modulo arithmetic
            dx = (next_x - head_x) % GRID_COUNT_X
            dy = (next_y - head_y) % GRID_COUNT_Y
            
            if dx == 1: self.direction = Direction.RIGHT
            elif dx == GRID_COUNT_X - 1: self.direction = Direction.LEFT
            elif dy == 1: self.direction = Direction.DOWN
            elif dy == GRID_COUNT_Y - 1: self.direction = Direction.UP

        # Move snake with optimized direction handling
        head_x, head_y = self.snake[0]
        if self.direction == Direction.RIGHT:
            new_head = ((head_x + 1) % GRID_COUNT_X, head_y)
        elif self.direction == Direction.LEFT:
            new_head = ((head_x - 1) % GRID_COUNT_X, head_y)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, (head_y + 1) % GRID_COUNT_Y)
        else:  # UP
            new_head = (head_x, (head_y - 1) % GRID_COUNT_Y)

        # Optimized collision check using set
        if new_head in set(self.snake):
            self.game_over = True
            return

        self.snake.appendleft(new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self):
        screen.fill(BLACK)
        
        # Batch draw calls for better performance
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, RED, food_rect)
        
        # Draw snake segments in one batch
        snake_rects = [pygame.Rect(
            segment[0] * GRID_SIZE,
            segment[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        ) for segment in self.snake]
        for rect in snake_rects:
            pygame.draw.rect(screen, GREEN, rect)
        
        pygame.display.flip()

def main():
    game = SnakeGame()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()

        game.update()
        game.draw()
        clock.tick(10)  # Control game speed

    pygame.quit()

if __name__ == "__main__":
    main()
