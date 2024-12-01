import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 400
CELL_SIZE = 20
SCORE_HEIGHT = 100  # Height for score display area

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SNAKE_HEAD = (0, 200, 0)  # Darker green for snake head
SNAKE_BODY = (50, 255, 50)  # Lighter green for snake body
SNAKE_BORDER = (0, 100, 0)  # Dark green border
SCORE_BG = (50, 50, 50)  # Dark gray for score background

# Directions
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']
MOVE_MAP = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# Snake Game
class SnakeGame:
    def __init__(self):
        self.snake = [(WIDTH // 2, HEIGHT // 2)]  # Start in the middle
        self.food = self.generate_food()
        self.direction = 'UP'
        self.score = 0
        self.best_score = 0

    def generate_food(self):
        while True:
            food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                   random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food not in self.snake:  # Make sure food doesn't spawn on snake
                return food

    def move_snake(self, direction):
        head_x, head_y = self.snake[0]
        move_x, move_y = MOVE_MAP[direction]
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)
        
        # Check if snake eats food
        if new_head == self.food:
            self.snake.insert(0, new_head)  # Add new head
            self.food = self.generate_food()
            self.score += 1
            if self.score > self.best_score:
                self.best_score = self.score
        else:
            self.snake = [new_head] + self.snake[:-1]

    def is_collision(self):
        head = self.snake[0]
        return (head in self.snake[1:] or
                head[0] < 0 or head[1] < 0 or
                head[0] >= WIDTH or head[1] >= HEIGHT)

    def compute_gradient(self):
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food

        # Compute partial derivatives
        dx = food_x - head_x
        dy = food_y - head_y

        # Normalize gradient
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude == 0:
            return 0, 0
        return dx / magnitude, dy / magnitude

    def choose_direction(self):
        gradient_x, gradient_y = self.compute_gradient()
        candidates = []

        # Evaluate each direction
        for direction, (dx, dy) in MOVE_MAP.items():
            # Simulate next position
            head_x, head_y = self.snake[0]
            next_x = head_x + dx * CELL_SIZE
            next_y = head_y + dy * CELL_SIZE
            
            # Skip if would cause collision
            if (next_x, next_y) in self.snake[1:] or \
               next_x < 0 or next_x >= WIDTH or \
               next_y < 0 or next_y >= HEIGHT:
                continue
                
            score = gradient_x * dx + gradient_y * dy  # Dot product
            candidates.append((score, direction))

        if not candidates:  # If no safe moves, try any move
            return random.choice(DIRECTIONS)
            
        # Choose the best direction
        return max(candidates, key=lambda x: x[0])[1]

# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Gradient Descent")
    font = pygame.font.Font(None, 36)
    game = SnakeGame()

    running = True
    while running:
        # Fill score area with dark background
        screen.fill(SCORE_BG)
        # Fill game area with black
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Choose next move using Gradient Descent
        game.direction = game.choose_direction()
        game.move_snake(game.direction)

        # Check collisions
        if game.is_collision():
            print(f"Game Over! Score: {game.score}")
            running = False

        # Draw snake with enhanced visuals
        for i, segment in enumerate(game.snake):
            adjusted_y = segment[1] + SCORE_HEIGHT
            if i == 0:  # Head
                pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                # Draw eyes
                eye_size = 4
                if game.direction == 'RIGHT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game.direction == 'LEFT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game.direction == 'UP':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                else:  # DOWN
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
            else:  # Body
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Draw food with enhanced visuals
        food_y = game.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Display scores
        score_text = font.render(f'Score: {game.score}', True, WHITE)
        best_score_text = font.render(f'Best Score: {game.best_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (WIDTH - best_score_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(10)

    # Keep window open after game ends
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()

if __name__ == "__main__":
    main()
