import pygame
import random
import math

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
            self.snake.insert(0, new_head)  # Add new head without removing tail
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

    def compute_distance(self, pos1, pos2):
        # Use Manhattan distance for simplicity
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def choose_direction_hill_climbing(self):
        head = self.snake[0]
        best_direction = None
        best_score = float('inf')  # We want to minimize distance

        for direction, (dx, dy) in MOVE_MAP.items():
            new_head = (head[0] + dx * CELL_SIZE, head[1] + dy * CELL_SIZE)
            # Check if the move is valid (no collision)
            if new_head in self.snake or new_head[0] < 0 or new_head[1] < 0 or \
               new_head[0] >= WIDTH or new_head[1] >= HEIGHT:
                continue

            # Compute distance to food
            distance = self.compute_distance(new_head, self.food)
            if distance < best_score:
                best_score = distance
                best_direction = direction

        # If no valid moves, pick a random direction (fallback)
        if best_direction is None:
            best_direction = random.choice(DIRECTIONS)

        return best_direction

# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    game = SnakeGame()
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        screen.fill(SCORE_BG)
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Choose next move using Hill Climbing
        game.direction = game.choose_direction_hill_climbing()
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
                eye_radius = 3
                pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                pygame.draw.circle(screen, WHITE, (segment[0] + 3*CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
            else:  # Body
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Draw food with enhanced visuals
        food_y = game.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Display scores
        score_text = font.render(f'Score: {game.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {game.best_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(10)

    # Wait for user to close window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()

if __name__ == "__main__":
    main()
