import pygame
import random

# Các tham số cài đặt cho game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Màu sắc
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Khởi tạo pygame
pygame.init()

# Biến toàn cục cho high score và generation
HIGH_SCORE = 0
GENERATION = 1

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Iterative Deepening DFS")
        
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Vị trí ban đầu của rắn
        self.direction = RIGHT
        self.food = self.random_food()
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.score = 0

    def random_food(self):
        while True:
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                return food_pos

    def draw_snake(self):
        # Vẽ thân rắn
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Vẽ mắt rắn
        head_x, head_y = self.snake[0]
        eye_radius = 3
        # Điều chỉnh vị trí mắt dựa trên hướng di chuyển
        if self.direction == RIGHT:
            left_eye = (head_x + CELL_SIZE - 5, head_y + 5)
            right_eye = (head_x + CELL_SIZE - 5, head_y + CELL_SIZE - 5)
        elif self.direction == LEFT:
            left_eye = (head_x + 5, head_y + 5)
            right_eye = (head_x + 5, head_y + CELL_SIZE - 5)
        elif self.direction == UP:
            left_eye = (head_x + 5, head_y + 5)
            right_eye = (head_x + CELL_SIZE - 5, head_y + 5)
        else:  # DOWN
            left_eye = (head_x + 5, head_y + CELL_SIZE - 5)
            right_eye = (head_x + CELL_SIZE - 5, head_y + CELL_SIZE - 5)
            
        pygame.draw.circle(self.screen, WHITE, left_eye, eye_radius)
        pygame.draw.circle(self.screen, WHITE, right_eye, eye_radius)

    def draw_food(self):
        # Vẽ thức ăn dạng hình tròn
        food_x, food_y = self.food
        center_x = food_x + CELL_SIZE // 2
        center_y = food_y + CELL_SIZE // 2
        pygame.draw.circle(self.screen, RED, (center_x, center_y), CELL_SIZE // 2)

    def move_snake(self):
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)
        self.snake = [new_head] + self.snake[:-1]

    def check_collision(self):
        global HIGH_SCORE, GENERATION
        head = self.snake[0]
        # Kiểm tra va chạm với bản thân hoặc tường
        if head in self.snake[1:] or not (0 <= head[0] < SCREEN_WIDTH and 0 <= head[1] < SCREEN_HEIGHT):
            if self.score > HIGH_SCORE:
                HIGH_SCORE = self.score
            self.reset_game()
        # Kiểm tra va chạm với thức ăn
        elif head == self.food:
            self.snake.append(self.snake[-1])  # Thêm một phần của rắn
            self.food = self.random_food()
            self.score += 1

    def reset_game(self):
        global GENERATION
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = RIGHT
        self.food = self.random_food()
        GENERATION += 1
        self.score = 0

    def iterative_deepening_dfs(self, start, goal, max_depth):
        """Sử dụng Iterative Deepening DFS để tìm đường đến thức ăn"""
        for depth_limit in range(max_depth):
            path = self.dfs_with_limit(start, goal, depth_limit)
            if path:
                return path
        return []

    def dfs_with_limit(self, start, goal, depth_limit):
        """DFS với độ sâu giới hạn"""
        stack = [(start, [], 0)]  # (vị trí, đường đi, độ sâu)
        visited = set()

        while stack:
            current_pos, path, depth = stack.pop()

            if depth > depth_limit:
                continue

            # Nếu chúng ta đã đến đích
            if current_pos == goal:
                return path

            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Các hướng di chuyển hợp lệ
            directions = [UP, DOWN, LEFT, RIGHT]
            for direction in directions:
                new_pos = (current_pos[0] + direction[0] * CELL_SIZE, current_pos[1] + direction[1] * CELL_SIZE)

                if (0 <= new_pos[0] < SCREEN_WIDTH and 
                    0 <= new_pos[1] < SCREEN_HEIGHT and 
                    new_pos not in self.snake[:-1]):  # Cho phép di chuyển vào vị trí đuôi rắn
                    stack.append((new_pos, path + [direction], depth + 1))

        return []  # Nếu không tìm được đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return
        
        # Tìm đường đi từ rắn đến thức ăn, tăng độ sâu tối đa lên 50
        path = self.iterative_deepening_dfs(self.snake[0], self.food, 50)

        # Di chuyển rắn theo các bước tìm được
        if path:
            self.direction = path[0]
            self.move_snake()
            self.check_collision()
        else:
            # Nếu không tìm được đường đi, reset game
            self.reset_game()

    def draw(self):
        """Vẽ lại màn hình game"""
        self.screen.fill(BLACK)
        self.draw_snake()
        self.draw_food()
        
        # Hiển thị điểm và generation
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {HIGH_SCORE}', True, WHITE)
        gen_text = font.render(f'Generation: {GENERATION}', True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(gen_text, (10, 90))
        
        pygame.display.flip()

    def main(self):
        """Vòng lặp chính của game"""
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            self.update()
            self.draw()
            self.clock.tick(10)  # Tốc độ game

        pygame.quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.main()
