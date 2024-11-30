import pygame
import random
import collections
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_COUNT = 20
GRID_SIZE = WINDOW_SIZE // GRID_COUNT
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Direction enum
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Snake Game - Linear Search')

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = collections.deque([(GRID_COUNT//2, GRID_COUNT//2)])
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if food not in self.snake:
                return food

    def linear_search(self):
        # Linear search implementation to find path to food
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # List all possible moves
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = (head_x + dx) % GRID_COUNT
            new_y = (head_y + dy) % GRID_COUNT
            new_pos = (new_x, new_y)
            
            if new_pos not in self.snake:
                # Calculate Manhattan distance to food
                distance = abs(new_x - food_x) + abs(new_y - food_y)
                possible_moves.append((distance, new_pos))
        
        if not possible_moves:
            return None
            
        # Linear search for the move with minimum distance to food
        best_move = possible_moves[0]
        for move in possible_moves[1:]:
            if move[0] < best_move[0]:
                best_move = move
                
        return best_move[1]

    def update(self):
        if self.game_over:
            return

        # Find next move using linear search
        next_move = self.linear_search()
        if next_move:
            head_x, head_y = self.snake[0]
            next_x, next_y = next_move
            
            # Determine direction based on next move
            if next_x == (head_x + 1) % GRID_COUNT:
                self.direction = Direction.RIGHT
            elif next_x == (head_x - 1) % GRID_COUNT:
                self.direction = Direction.LEFT
            elif next_y == (head_y + 1) % GRID_COUNT:
                self.direction = Direction.DOWN
            elif next_y == (head_y - 1) % GRID_COUNT:
                self.direction = Direction.UP

        # Move snake
        head_x, head_y = self.snake[0]
        if self.direction == Direction.RIGHT:
            new_head = ((head_x + 1) % GRID_COUNT, head_y)
        elif self.direction == Direction.LEFT:
            new_head = ((head_x - 1) % GRID_COUNT, head_y)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, (head_y + 1) % GRID_COUNT)
        else:  # UP
            new_head = (head_x, (head_y - 1) % GRID_COUNT)

        # Check collision with self
        if new_head in self.snake:
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
        
        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, RED, food_rect)
        
        # Draw snake
        for segment in self.snake:
            snake_rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(screen, GREEN, snake_rect)
        
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
