import pygame
import random
import collections
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE_X = 600
WINDOW_SIZE_Y = 300
GRID_COUNT_X = 30
GRID_COUNT_Y = 15
GRID_SIZE = WINDOW_SIZE_Y // GRID_COUNT_Y
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# Direction enum
class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption('Snake Game - Binary Search')

# Initialize fonts
pygame.font.init()
game_font = pygame.font.Font(None, 36)

class SnakeGame:
    def __init__(self):
        self.reset()
        self.high_score = self.load_high_score()

    def reset(self):
        self.snake = collections.deque([(GRID_COUNT_X//2, GRID_COUNT_Y//2)])
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        try:
            with open("binary_search_high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("binary_search_high_score.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT_X-1), random.randint(0, GRID_COUNT_Y-1))
            if food not in self.snake:
                return food

    def binary_search(self):
        # Binary search implementation to find path to food
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Get all possible moves
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = (head_x + dx) % GRID_COUNT_X
            new_y = (head_y + dy) % GRID_COUNT_Y
            new_pos = (new_x, new_y)
            
            if new_pos not in self.snake:
                # Calculate Manhattan distance to food
                distance = abs(new_x - food_x) + abs(new_y - food_y)
                possible_moves.append((distance, new_pos))
        
        if not possible_moves:
            return None
            
        # Sort moves by distance
        possible_moves.sort(key=lambda x: x[0])
        
        # Binary search for the best move
        left = 0
        right = len(possible_moves) - 1
        
        while left <= right:
            mid = (left + right) // 2
            current_move = possible_moves[mid]
            
            # If this move leads directly to food, take it
            if current_move[0] == 0:
                return current_move[1]
                
            # Check if next move would be worse
            if mid + 1 < len(possible_moves) and possible_moves[mid + 1][0] > current_move[0]:
                return current_move[1]
                
            # Move search window based on distance comparison
            if current_move[0] > possible_moves[left][0]:
                right = mid - 1
            else:
                left = mid + 1
                
        # Return the first move if no better option found
        return possible_moves[0][1]

    def update(self):
        if self.game_over:
            return

        # Find next move using binary search
        next_move = self.binary_search()
        if next_move:
            head_x, head_y = self.snake[0]
            next_x, next_y = next_move
            
            # Determine direction based on next move
            if next_x == (head_x + 1) % GRID_COUNT_X:
                self.direction = Direction.RIGHT
            elif next_x == (head_x - 1) % GRID_COUNT_X:
                self.direction = Direction.LEFT
            elif next_y == (head_y + 1) % GRID_COUNT_Y:
                self.direction = Direction.DOWN
            elif next_y == (head_y - 1) % GRID_COUNT_Y:
                self.direction = Direction.UP

        # Move snake
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
            self.save_high_score()
            return

        self.snake.appendleft(new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
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
        
        # Draw food with glow effect
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(screen, (200, 0, 0), food_rect)  # Darker red core
        pygame.draw.rect(screen, RED, food_rect.inflate(-4, -4))  # Brighter red center
        
        # Draw snake with gradient effect
        for i, segment in enumerate(self.snake):
            intensity = 255 - (i * 5)  # Gradient from bright to darker green
            if intensity < 50: intensity = 50  # Minimum brightness
            color = (0, intensity, 0)
            snake_rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(screen, color, snake_rect)
            pygame.draw.rect(screen, (0, min(intensity + 50, 255), 0), snake_rect.inflate(-4, -4))

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
                if event.key == pygame.K_r:
                    game.reset()

        game.update()
        game.draw()
        clock.tick(10)  # Control game speed

    pygame.quit()

if __name__ == "__main__":
    main()
