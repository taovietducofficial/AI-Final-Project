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
WINDOW_SIZE_X = 600  # Increased window size
WINDOW_SIZE_Y = 300
GRID_COUNT_X = 30
GRID_COUNT_Y = 15
GRID_SIZE = WINDOW_SIZE_Y // GRID_COUNT_Y

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) 
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption('Snake Game - Blind Search')

# Load and set game icon
icon = pygame.Surface((32, 32))
icon.fill(GREEN)
pygame.display.set_icon(icon)

# Initialize fonts
pygame.font.init()
game_font = pygame.font.Font(None, 36)

class SnakeGame:
    def __init__(self):
        self.reset()
        self.high_score = self.load_high_score()

    def reset(self):
        # Initial snake position (middle of screen)
        self.snake = collections.deque([(GRID_COUNT_X//2, GRID_COUNT_Y//2)])
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("high_score.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def generate_food(self):
        # Generate food position randomly, avoiding snake body
        while True:
            food = (random.randint(0, GRID_COUNT_X-1), random.randint(0, GRID_COUNT_Y-1))
            if food not in self.snake:
                return food

    def blind_search(self):
        # Implement blind search (BFS) to find path to food
        # This search doesn't know the target location until it's found
        queue = collections.deque([(self.snake[0], [])])
        visited = {self.snake[0]}
        
        while queue:
            current, path = queue.popleft()
            
            # Try all possible directions blindly
            for direction in Direction:
                if direction == Direction.UP:
                    next_pos = (current[0], (current[1] - 1) % GRID_COUNT_Y)
                elif direction == Direction.DOWN:
                    next_pos = (current[0], (current[1] + 1) % GRID_COUNT_Y)
                elif direction == Direction.LEFT:
                    next_pos = ((current[0] - 1) % GRID_COUNT_X, current[1])
                else:  # RIGHT
                    next_pos = ((current[0] + 1) % GRID_COUNT_X, current[1])
                
                # Check if position is valid and not visited
                if next_pos not in visited and next_pos not in self.snake:
                    visited.add(next_pos)
                    new_path = path + [next_pos]
                    
                    # Found food
                    if next_pos == self.food:
                        return new_path[0] if new_path else None
                        
                    queue.append((next_pos, new_path))
        return None

    def update(self):
        if self.game_over:
            return

        # Get next move from blind search
        next_move = self.blind_search()
        if next_move:
            # Determine direction based on next move
            head_x, head_y = self.snake[0]
            next_x, next_y = next_move
            
            # Update direction based on next move
            if (next_x - head_x) % GRID_COUNT_X == 1:
                self.direction = Direction.RIGHT
            elif (next_x - head_x) % GRID_COUNT_X == GRID_COUNT_X - 1:
                self.direction = Direction.LEFT
            elif (next_y - head_y) % GRID_COUNT_Y == 1:
                self.direction = Direction.DOWN
            elif (next_y - head_y) % GRID_COUNT_Y == GRID_COUNT_Y - 1:
                self.direction = Direction.UP

        # Move snake based on current direction
        head_x, head_y = self.snake[0]
        if self.direction == Direction.RIGHT:
            new_head = ((head_x + 1) % GRID_COUNT_X, head_y)
        elif self.direction == Direction.LEFT:
            new_head = ((head_x - 1) % GRID_COUNT_X, head_y)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, (head_y + 1) % GRID_COUNT_Y)
        else:  # UP
            new_head = (head_x, (head_y - 1) % GRID_COUNT_Y)

        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        self.snake.appendleft(new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw grid lines
        for x in range(0, WINDOW_SIZE_X, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_SIZE_Y))
        for y in range(0, WINDOW_SIZE_Y, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WINDOW_SIZE_X, y))
        
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

        # Draw score and high score
        score_text = game_font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = game_font.render(f'High Score: {self.high_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))

        # Draw game over message
        if self.game_over:
            game_over_text = game_font.render('Game Over! Press R to Restart', True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE_X//2, WINDOW_SIZE_Y//2))
            screen.blit(game_over_text, text_rect)
        
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
                if event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update()
        game.draw()
        clock.tick(10)  # Control game speed

    pygame.quit()

if __name__ == "__main__":
    main()
