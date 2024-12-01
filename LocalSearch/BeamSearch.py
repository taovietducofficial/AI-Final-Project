import pygame
import random
from collections import deque

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
DIRECTIONS = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# Game state
class GameState:
    def __init__(self, snake, food, direction):
        self.snake = snake  # List of tuples (x, y)
        self.food = food  # Tuple (x, y)
        self.direction = direction  # Current direction
        self.score = len(snake) - 1  # Score is snake length minus initial length

    def next_state(self, action):
        head_x, head_y = self.snake[0]
        move_x, move_y = DIRECTIONS[action]
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)
        
        new_snake = [new_head] + self.snake[:-1]
        if new_head == self.food:
            new_snake.append(self.snake[-1])  # Grow the snake
        return GameState(new_snake, self.food, action)

    def is_valid(self, width, height):
        head = self.snake[0]
        return (0 <= head[0] < width and 0 <= head[1] < height and
                len(self.snake) == len(set(self.snake)))  # No collision with itself

    def heuristic(self):
        head = self.snake[0]
        food = self.food
        return abs(head[0] - food[0]) + abs(head[1] - food[1])  # Manhattan distance

# Beam Search
def beam_search(game_state, width, height, beam_width=3, depth=10):
    beam = deque([game_state])  # Start with the current state

    for _ in range(depth):
        candidates = []
        for state in beam:
            for action in DIRECTIONS.keys():
                next_state = state.next_state(action)
                if next_state.is_valid(width, height):
                    candidates.append(next_state)

        # Sort by heuristic and keep top-k
        candidates.sort(key=lambda s: s.heuristic())
        beam = deque(candidates[:beam_width])

    # Return the best state
    return beam[0] if beam else None

# Initialize game
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))  # Add extra height for score
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Beam Search")

    # Font for score display
    font = pygame.font.Font(None, 36)
    
    # High score tracking
    high_score = 0

    # Initial snake and food
    snake = [(WIDTH // 2, HEIGHT // 2)]
    food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)

    game_state = GameState(snake, food, 'UP')
    running = True

    while running:
        # Fill score area with dark background
        screen.fill(SCORE_BG)
        # Fill game area with black
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Beam Search to decide next move
        next_state = beam_search(game_state, WIDTH, HEIGHT)
        if next_state:
            game_state = next_state
            # Update high score
            high_score = max(high_score, game_state.score)
        else:
            print("Game Over!")
            running = False

        # Draw snake with enhanced visuals
        for i, segment in enumerate(game_state.snake):
            # Adjust y-coordinate for game area offset
            adjusted_y = segment[1] + SCORE_HEIGHT
            # Draw snake body segments with border
            if i == 0:  # Head
                pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                # Draw eyes
                eye_size = 4
                if game_state.direction == 'RIGHT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game_state.direction == 'LEFT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game_state.direction == 'UP':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                else:  # DOWN
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
            else:  # Body
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Draw food with enhanced visuals (adjust y-coordinate)
        food_y = game_state.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Display scores in score area
        score_text = font.render(f'Score: {game_state.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        # Update display
        pygame.display.flip()
        clock.tick(10)

    # Keep window open after game ends
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    main()
