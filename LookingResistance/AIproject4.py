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
pygame.display.set_caption('Snake Game - Looking Resistance')

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
        self.resistance_points = []  # Points that resist/block the snake's path
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def load_high_score(self):
        try:
            with open("resistance_high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("resistance_high_score.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT_X-1), random.randint(0, GRID_COUNT_Y-1))
            if food not in self.snake and food not in self.resistance_points:
                return food
                
    def generate_resistance(self):
        # Generate resistance points that try to block optimal paths
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Clear old resistance points
        self.resistance_points = []
        
        # Try to place resistance points between snake and food
        for _ in range(3):  # Place 3 resistance points
            mid_x = (head_x + food_x) // 2 + random.randint(-2, 2)
            mid_y = (head_y + food_y) // 2 + random.randint(-2, 2)
            
            # Ensure points are within bounds
            mid_x = mid_x % GRID_COUNT_X
            mid_y = mid_y % GRID_COUNT_Y
            
            resistance_point = (mid_x, mid_y)
            if resistance_point not in self.snake and resistance_point != self.food:
                self.resistance_points.append(resistance_point)

    def looking_resistance_search(self):
        # Implementation of adversarial search considering resistance points
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Get all possible moves
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = (head_x + dx) % GRID_COUNT_X
            new_y = (head_y + dy) % GRID_COUNT_Y
            new_pos = (new_x, new_y)
            
            if new_pos not in self.snake and new_pos not in self.resistance_points:
                # Calculate weighted score based on:
                # 1. Distance to food
                # 2. Distance to nearest resistance point
                food_distance = abs(new_x - food_x) + abs(new_y - food_y)
                
                # Find minimum distance to resistance points
                min_resistance_dist = GRID_COUNT_X * 2  # Max possible distance
                for rx, ry in self.resistance_points:
                    resistance_dist = abs(new_x - rx) + abs(new_y - ry)
                    min_resistance_dist = min(min_resistance_dist, resistance_dist)
                
                # Score = food distance - resistance distance weight
                # Lower score is better
                score = food_distance - (min_resistance_dist * 0.5)
                possible_moves.append((score, new_pos))
        
        if not possible_moves:
            return None
            
        # Find move with best score
        best_move = min(possible_moves, key=lambda x: x[0])
        return best_move[1]

    def update(self):
        if self.game_over:
            return

        # Generate new resistance points periodically
        if random.random() < 0.1:  # 10% chance each update
            self.generate_resistance()

        # Find next move using looking resistance search
        next_move = self.looking_resistance_search()
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

        # Check collision with self or resistance points
        if new_head in self.snake or new_head in self.resistance_points:
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
        
        # Draw resistance points with pulsing effect
        for point in self.resistance_points:
            resistance_rect = pygame.Rect(
                point[0] * GRID_SIZE,
                point[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500  # 0 to 1 pulsing value
            blue_value = int(200 + 55 * pulse)  # Pulsing blue intensity
            pygame.draw.rect(screen, (0, 0, blue_value), resistance_rect)
            pygame.draw.rect(screen, BLUE, resistance_rect.inflate(-4, -4))
        
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
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
                
        game.update()
        game.draw()
        clock.tick(10)  # Control game speed
    
    pygame.quit()

if __name__ == "__main__":
    main()
