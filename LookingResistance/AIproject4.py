import pygame
import random
import collections
from enum import Enum
import heapq

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
        # Cache movement vectors for faster lookup
        self.movement_vectors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        # Pre-calculate grid positions
        self.grid_positions = set((x, y) for x in range(GRID_COUNT_X) for y in range(GRID_COUNT_Y))
        self.reset()
        self.high_score = self.load_high_score()

    def reset(self):
        # Initialize snake at center
        self.snake = collections.deque([(GRID_COUNT_X//2, GRID_COUNT_Y//2)])
        self.direction = Direction.RIGHT
        # Initialize resistance points that block snake's path
        self.resistance_points = []
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        # Cache for resistance calculations
        self.resistance_cache = {}

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
        # Generate food in available positions
        available_positions = self.grid_positions - set(self.snake) - set(self.resistance_points)
        return random.choice(tuple(available_positions))
                
    def generate_resistance(self):
        # Get current head and food positions
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Clear old resistance points and cache
        self.resistance_points = []
        self.resistance_cache.clear()
        
        # Calculate optimal path area between head and food
        path_area = set()
        min_x, max_x = sorted([head_x, food_x])
        min_y, max_y = sorted([head_y, food_y])
        
        # Expand area by 2 in each direction to create resistance zone
        for x in range(max(0, min_x - 2), min(GRID_COUNT_X, max_x + 3)):
            for y in range(max(0, min_y - 2), min(GRID_COUNT_Y, max_y + 3)):
                path_area.add((x, y))
        
        # Generate resistance points in path area
        available_positions = path_area - set(self.snake) - {self.food}
        num_points = min(3, len(available_positions))
        self.resistance_points = random.sample(tuple(available_positions), num_points)

    def manhattan_distance(self, pos1, pos2):
        # Calculate Manhattan distance between two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def looking_resistance_search(self):
        # Get current head position
        head = self.snake[0]
        
        # Return cached result if available
        if head in self.resistance_cache:
            return self.resistance_cache[head]
            
        # A* pathfinding implementation
        frontier = [(self.manhattan_distance(head, self.food), 0, head, [])]
        visited = {head}
        
        while frontier:
            _, cost, current, path = heapq.heappop(frontier)
            
            # Return next position if food found
            if current == self.food:
                next_pos = path[0] if path else current
                self.resistance_cache[head] = next_pos
                return next_pos
                
            # Explore neighboring positions
            for dx, dy in self.movement_vectors:
                next_x = (current[0] + dx) % GRID_COUNT_X
                next_y = (current[1] + dy) % GRID_COUNT_Y
                next_pos = (next_x, next_y)
                
                # Check if position is valid
                if next_pos not in visited and next_pos not in self.snake and next_pos not in self.resistance_points:
                    visited.add(next_pos)
                    new_path = [next_pos] + path if not path else path
                    new_cost = cost + 1
                    priority = new_cost + self.manhattan_distance(next_pos, self.food)
                    heapq.heappush(frontier, (priority, new_cost, next_pos, new_path))
        
        # If no path found, find safe move
        return self.find_safe_move(head)
        
    def find_safe_move(self, head):
        # Initialize variables for best move
        best_move = None
        best_score = float('-inf')
        
        # Check all possible moves
        for dx, dy in self.movement_vectors:
            new_x = (head[0] + dx) % GRID_COUNT_X
            new_y = (head[1] + dy) % GRID_COUNT_Y
            new_pos = (new_x, new_y)
            
            # Score move based on available space and food distance
            if new_pos not in self.snake and new_pos not in self.resistance_points:
                space_score = len(self.get_available_space(new_pos))
                food_score = -self.manhattan_distance(new_pos, self.food)
                total_score = space_score + food_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_move = new_pos
                    
        return best_move
        
    def get_available_space(self, pos):
        # Use flood fill to count available space
        space = set()
        queue = collections.deque([pos])
        
        while queue and len(space) < 10:  # Limit check to nearby area
            current = queue.popleft()
            if current not in space:
                space.add(current)
                
                # Check neighboring positions
                for dx, dy in self.movement_vectors:
                    next_x = (current[0] + dx) % GRID_COUNT_X
                    next_y = (current[1] + dy) % GRID_COUNT_Y
                    next_pos = (next_x, next_y)
                    
                    if next_pos not in space and next_pos not in self.snake and next_pos not in self.resistance_points:
                        queue.append(next_pos)
                        
        return space

    def update(self):
        if self.game_over:
            return

        # Generate new resistance points with 10% chance
        if random.random() < 0.1:
            self.generate_resistance()

        # Find next move using looking resistance search
        next_move = self.looking_resistance_search()
        if next_move:
            head_x, head_y = self.snake[0]
            next_x, next_y = next_move
            
            # Update direction based on next move
            dx = (next_x - head_x) % GRID_COUNT_X
            dy = (next_y - head_y) % GRID_COUNT_Y
            
            if dx == 1: self.direction = Direction.RIGHT
            elif dx == GRID_COUNT_X - 1: self.direction = Direction.LEFT
            elif dy == 1: self.direction = Direction.DOWN
            elif dy == GRID_COUNT_Y - 1: self.direction = Direction.UP

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
            self.resistance_cache.clear()  # Clear cache when food position changes
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
