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
pygame.display.set_caption('Snake Game - Seeking Comfort')

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
        self.comfort_zones = []  # Areas that are considered "comfortable" for the snake

    def load_high_score(self):
        try:
            with open("comfort_high_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open("comfort_high_score.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT_X-1), random.randint(0, GRID_COUNT_Y-1))
            if food not in self.snake:
                return food

    def generate_comfort_zones(self):
        # Generate comfort zones near walls and corners
        self.comfort_zones = []
        
        # Add corners as comfort zones
        corners = [(0,0), (0,GRID_COUNT_Y-1), (GRID_COUNT_X-1,0), (GRID_COUNT_X-1,GRID_COUNT_Y-1)]
        self.comfort_zones.extend(corners)
        
        # Add some random comfort zones
        for _ in range(3):
            zone = (random.randint(0, GRID_COUNT_X-1), random.randint(0, GRID_COUNT_Y-1))
            if zone not in self.snake and zone != self.food:
                self.comfort_zones.append(zone)

    def comfort_seeking_search(self):
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Get all possible moves
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = (head_x + dx) % GRID_COUNT_X
            new_y = (head_y + dy) % GRID_COUNT_Y
            new_pos = (new_x, new_y)
            
            if new_pos not in self.snake:
                # Calculate weighted score based on:
                # 1. Distance to food
                # 2. Distance to nearest comfort zone
                food_distance = abs(new_x - food_x) + abs(new_y - food_y)
                
                # Find distance to nearest comfort zone
                comfort_distance = float('inf')
                for zone in self.comfort_zones:
                    dist = abs(new_x - zone[0]) + abs(new_y - zone[1])
                    comfort_distance = min(comfort_distance, dist)
                
                # Weight food distance more when score is low
                # Weight comfort zones more when score is high
                if self.score < 5:
                    score = food_distance + 0.5 * comfort_distance
                else:
                    score = 0.5 * food_distance + comfort_distance
                    
                possible_moves.append((score, new_pos))
        
        if not possible_moves:
            return None
            
        # Choose move with lowest score
        best_move = min(possible_moves, key=lambda x: x[0])
        return best_move[1]

    def update(self):
        if self.game_over:
            return

        # Regenerate comfort zones periodically
        if self.score % 5 == 0:
            self.generate_comfort_zones()

        # Find next move using comfort seeking search
        next_move = self.comfort_seeking_search()
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
        # Draw background with grid lines
        screen.fill(BLACK)
        for x in range(0, WINDOW_SIZE_X, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_SIZE_Y))
        for y in range(0, WINDOW_SIZE_Y, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WINDOW_SIZE_X, y))
        
        # Draw comfort zones with glow effect
        for zone in self.comfort_zones:
            zone_rect = pygame.Rect(
                zone[0] * GRID_SIZE,
                zone[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            glow_rect = zone_rect.inflate(4, 4)
            pygame.draw.rect(screen, (0, 80, 0), glow_rect)  # Outer glow
            pygame.draw.rect(screen, (0, 120, 0), zone_rect)  # Inner color
        
        # Draw food with pulsing effect
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE,
            self.food[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500  # Pulsing value between 0 and 1
        food_color = (255, int(pulse * 200), int(pulse * 200))  # Pulsing red
        pygame.draw.rect(screen, food_color, food_rect)
        
        # Draw snake with gradient effect
        for i, segment in enumerate(self.snake):
            intensity = 255 - (i * 5)  # Gradient from bright to darker green
            if intensity < 50: intensity = 50  # Minimum brightness
            segment_rect = pygame.Rect(
                segment[0] * GRID_SIZE,
                segment[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(screen, (0, intensity, 0), segment_rect)
            pygame.draw.rect(screen, (0, min(intensity + 50, 255), 0), segment_rect.inflate(-4, -4))

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
