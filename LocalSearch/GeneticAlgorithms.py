import pygame
import random
import numpy as np

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

# Genetic Algorithm parameters
POPULATION_SIZE = 100  # Tăng kích thước quần thể
GENOME_LENGTH = 50    # Tăng độ dài genome
MUTATION_RATE = 0.2   # Tăng tỷ lệ đột biến
NUM_GENERATIONS = 200 # Tăng số thế hệ

# Game state
class GameState:
    def __init__(self, snake, food, direction):
        self.snake = snake
        self.food = food
        self.direction = direction
        self.score = len(snake) - 1

    def next_state(self, action):
        head_x, head_y = self.snake[0]
        move_x, move_y = MOVE_MAP[action]
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)
        
        new_snake = [new_head] + self.snake[:-1]
        if new_head == self.food:
            new_snake.append(self.snake[-1])  # Grow the snake
            # Tạo thức ăn mới khi rắn ăn
            self.food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                        random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
        return GameState(new_snake, self.food, action)

    def is_valid(self, width, height):
        head = self.snake[0]
        return (0 <= head[0] < width and 0 <= head[1] < height and
                len(self.snake) == len(set(self.snake)))  # No collision with itself

    def fitness(self):
        head = self.snake[0]
        # Cải thiện hàm fitness
        distance = -abs(head[0] - self.food[0]) - abs(head[1] - self.food[1])  # Manhattan distance
        score_bonus = self.score * 1000  # Thưởng điểm cho việc ăn được mồi
        return distance + score_bonus

# Genetic Algorithm
def create_population():
    return [random.choices(DIRECTIONS, k=GENOME_LENGTH) for _ in range(POPULATION_SIZE)]

def evaluate_population(population, game_state, width, height):
    scores = []
    for genome in population:
        state = game_state
        steps = 0
        for action in genome:
            if not state.is_valid(width, height):
                break
            next_state = state.next_state(action)
            if next_state.score > state.score:  # Nếu ăn được mồi
                steps = 0  # Reset số bước
            else:
                steps += 1
            if steps > 50:  # Nếu đi quá nhiều bước không ăn được mồi
                break
            state = next_state
        scores.append(state.fitness())
    return scores

def select_population(population, scores):
    # Tournament selection
    selected = []
    for _ in range(POPULATION_SIZE // 2):
        tournament = random.sample(list(zip(scores, population)), 5)
        winner = max(tournament, key=lambda x: x[0])[1]
        selected.append(winner)
    return selected

def crossover(parent1, parent2):
    # Two-point crossover
    point1, point2 = sorted(random.sample(range(GENOME_LENGTH), 2))
    child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    return child

def mutate(genome):
    mutated = genome.copy()
    for i in range(len(mutated)):
        if random.random() < MUTATION_RATE:
            mutated[i] = random.choice(DIRECTIONS)
    return mutated

def next_generation(selected_population):
    new_population = []
    while len(new_population) < POPULATION_SIZE:
        parent1, parent2 = random.sample(selected_population, 2)
        child1 = mutate(crossover(parent1, parent2))
        child2 = mutate(crossover(parent2, parent1))
        new_population.extend([child1, child2])
    return new_population[:POPULATION_SIZE]

# Initialize game
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Genetic Algorithm")

    # Font for score display
    font = pygame.font.Font(None, 36)

    # Initial snake and food
    snake = [(WIDTH // 2, HEIGHT // 2)]
    food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)

    game_state = GameState(snake, food, 'UP')
    running = True
    best_score = 0

    # Genetic Algorithm
    population = create_population()

    for generation in range(NUM_GENERATIONS):
        scores = evaluate_population(population, game_state, WIDTH, HEIGHT)
        selected_population = select_population(population, scores)
        population = next_generation(selected_population)

        # Use the best genome for the next move
        best_genome = selected_population[0]
        for action in best_genome:
            game_state = game_state.next_state(action)
            if not game_state.is_valid(WIDTH, HEIGHT):
                running = False
                break

            # Drawing
            # Fill score area with dark background
            screen.fill(SCORE_BG)
            # Fill game area with black
            pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

            # Draw snake with enhanced visuals
            for i, segment in enumerate(game_state.snake):
                # Adjust y-coordinate for game area offset
                adjusted_y = segment[1] + SCORE_HEIGHT
                # Draw snake body segments with border
                if i == 0:  # Head
                    pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                    # Vẽ mắt cho rắn
                    eye_radius = 3
                    # Mắt trái
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                    # Mắt phải
                    pygame.draw.circle(screen, WHITE, (segment[0] + 3*CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                else:  # Body
                    pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

            # Draw food with enhanced visuals
            food_y = game_state.food[1] + SCORE_HEIGHT
            pygame.draw.circle(screen, RED, (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
            pygame.draw.circle(screen, (200, 0, 0), (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)
            
            # Display scores in score area
            score_text = font.render(f'Score: {game_state.score}', True, WHITE)
            high_score_text = font.render(f'High Score: {best_score}', True, WHITE)
            gen_text = font.render(f'Generation: {generation}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))
            screen.blit(gen_text, (10, 40))
            
            pygame.display.flip()
            clock.tick(20)  # Tăng tốc độ game

            if game_state.score > best_score:
                best_score = game_state.score
                print(f"New high score {best_score} at generation {generation}")

        if not running:
            break

    print(f"Game Over! Final Score: {game_state.score}")
    
    # Đợi cho đến khi người dùng đóng cửa sổ
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
