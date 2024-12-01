import pygame
import random
import heapq

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


class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Uniform Cost Search")
        
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Vị trí ban đầu của rắn
        self.direction = RIGHT
        self.food = self.random_food()
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.high_score = 0
        self.generation = 1
        self.score = 0

    def random_food(self):
        while True:
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:
                return food_pos

    def draw_snake(self):
        # Vẽ thân rắn
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Vẽ mắt rắn (chỉ khi rắn còn sống)
        if not self.game_over:
            head = self.snake[0]
            eye_size = 4
            # Mắt trái
            eye_left = (head[0] + 5, head[1] + 5)
            pygame.draw.circle(self.screen, WHITE, eye_left, eye_size)
            # Mắt phải
            eye_right = (head[0] + 15, head[1] + 5)
            pygame.draw.circle(self.screen, WHITE, eye_right, eye_size)

    def draw_food(self):
        # Vẽ thức ăn dạng hình tròn
        food_center = (self.food[0] + CELL_SIZE//2, self.food[1] + CELL_SIZE//2)
        pygame.draw.circle(self.screen, RED, food_center, CELL_SIZE//2)

    def move_snake(self):
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)
        
        # Kiểm tra xuyên tường
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)
        self.snake = [new_head] + self.snake[:-1]

    def check_collision(self):
        head = self.snake[0]
        # Kiểm tra va chạm với bản thân
        if head in self.snake[1:]:
            if self.score > self.high_score:
                self.high_score = self.score
            self.generation += 1
            self.reset_game()
        # Kiểm tra va chạm với thức ăn
        if head == self.food:
            self.snake.append(self.snake[-1])  # Thêm một phần của rắn
            self.food = self.random_food()
            self.score += 1

    def reset_game(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = RIGHT
        self.food = self.random_food()
        self.score = 0

    def uniform_cost_search(self, start, goal):
        """Tìm đường đi bằng thuật toán Uniform Cost Search"""
        pq = []  # Priority Queue
        heapq.heappush(pq, (0, start, []))  # (cost, position, path)
        visited = set()

        while pq:
            cost, current_pos, path = heapq.heappop(pq)

            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Nếu đến được mục tiêu
            if current_pos == goal:
                return path

            # Các hướng di chuyển hợp lệ
            directions = [UP, DOWN, LEFT, RIGHT]
            for direction in directions:
                new_pos = (
                    (current_pos[0] + direction[0] * CELL_SIZE) % SCREEN_WIDTH,
                    (current_pos[1] + direction[1] * CELL_SIZE) % SCREEN_HEIGHT
                )

                if new_pos not in visited and new_pos not in self.snake[1:]:
                    heapq.heappush(pq, (cost + 1, new_pos, path + [direction]))

        return []  # Không tìm được đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        # Tìm đường đi từ rắn đến thức ăn
        path = self.uniform_cost_search(self.snake[0], self.food)

        # Di chuyển rắn theo các bước tìm được
        if path:
            self.direction = path[0]
            self.move_snake()
            self.check_collision()

    def draw(self):
        """Vẽ lại màn hình game"""
        self.screen.fill(BLACK)
        self.draw_snake()
        self.draw_food()
        
        # Hiển thị điểm và thế hệ
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {self.high_score}', True, WHITE)
        generation_text = font.render(f'Generation: {self.generation}', True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(generation_text, (10, 90))
        
        pygame.display.flip()

    def main(self):
        """Vòng lặp chính của game"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()
            self.draw()
            self.clock.tick(10)  # Tốc độ game

        pygame.quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.main()
