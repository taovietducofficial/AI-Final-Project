import pygame
import random
from collections import deque

# Kích thước của màn hình game
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCORE_HEIGHT = 50  # Chiều cao phần hiển thị điểm
CELL_SIZE = 20

# Màu sắc
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
SCORE_BG = (50, 50, 50)  # Màu nền phần hiển thị điểm
SNAKE_HEAD = (0, 200, 0)  # Màu đầu rắn
SNAKE_BODY = (0, 255, 0)  # Màu thân rắn

# Hướng di chuyển
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Khởi tạo pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + SCORE_HEIGHT))
pygame.display.set_caption("Snake Game with BFS")
clock = pygame.time.Clock()

# Lớp game Snake
class SnakeGame:
    def __init__(self):
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]  # Vị trí đầu tiên của rắn
        self.direction = RIGHT
        self.food = None
        self.generate_food()
        self.game_over = False
        self.score = 0
        self.best_score = 0
        self.generation = 1

    def generate_food(self):
        """Tạo ra quả táo ngẫu nhiên trên bàn cờ"""
        while True:
            food = (random.randrange(0, SCREEN_WIDTH, CELL_SIZE), 
                   random.randrange(0, SCREEN_HEIGHT, CELL_SIZE))
            if food not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                self.food = food
                break

    def move_snake(self):
        """Di chuyển rắn"""
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)

        # Kiểm tra va chạm với chính mình hoặc tường
        if new_head in self.snake or not (0 <= new_head[0] < SCREEN_WIDTH and 0 <= new_head[1] < SCREEN_HEIGHT):
            if self.score > self.best_score:
                self.best_score = self.score
            self.game_over = True
            return False

        self.snake.insert(0, new_head)

        # Kiểm tra nếu rắn ăn táo
        if new_head == self.food:
            self.score += 1
            self.generate_food()  # Tạo ra táo mới
        else:
            self.snake.pop()  # Rắn di chuyển

        return True

    def bfs(self):
        """Sử dụng thuật toán BFS để tìm đường ngắn nhất đến táo"""
        start = self.snake[0]
        goal = self.food

        # Các hướng di chuyển hợp lệ
        directions = [UP, DOWN, LEFT, RIGHT]
        queue = deque([(start, [])])  # Lưu trữ các node và đường đi đến node đó
        visited = set()
        visited.add(start)

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path  # Trả về đường đi đến táo

            for direction in directions:
                new_pos = (current[0] + direction[0] * CELL_SIZE, current[1] + direction[1] * CELL_SIZE)
                if 0 <= new_pos[0] < SCREEN_WIDTH and 0 <= new_pos[1] < SCREEN_HEIGHT and new_pos not in visited and new_pos not in self.snake:
                    queue.append((new_pos, path + [direction]))
                    visited.add(new_pos)

        return []  # Không tìm thấy đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return

        # Sử dụng BFS để tìm đường đi
        path = self.bfs()

        if path:
            self.direction = path[0]  # Di chuyển theo hướng đầu tiên trong đường đi

        # Di chuyển rắn
        if not self.move_snake():
            self.game_over = True

    def draw(self):
        """Vẽ lại màn hình"""
        # Vẽ phần hiển thị điểm
        screen.fill(SCORE_BG, (0, 0, SCREEN_WIDTH, SCORE_HEIGHT))
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        best_text = font.render(f'Best: {self.best_score}', True, WHITE)
        gen_text = font.render(f'Generation: {self.generation}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(best_text, (200, 10))
        screen.blit(gen_text, (400, 10))

        # Vẽ phần game
        screen.fill(BLACK, (0, SCORE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Vẽ rắn
        for i, segment in enumerate(self.snake):
            if i == 0:  # Đầu rắn
                pygame.draw.rect(screen, SNAKE_HEAD, 
                               (segment[0], segment[1] + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))
                # Vẽ mắt
                eye_radius = 3
                pygame.draw.circle(screen, WHITE, 
                                 (segment[0] + CELL_SIZE//4, segment[1] + SCORE_HEIGHT + CELL_SIZE//3), 
                                 eye_radius)
                pygame.draw.circle(screen, WHITE, 
                                 (segment[0] + 3*CELL_SIZE//4, segment[1] + SCORE_HEIGHT + CELL_SIZE//3), 
                                 eye_radius)
            else:  # Thân rắn
                pygame.draw.rect(screen, SNAKE_BODY, 
                               (segment[0], segment[1] + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))

        # Vẽ táo
        pygame.draw.circle(screen, RED, 
                         (self.food[0] + CELL_SIZE//2, self.food[1] + SCORE_HEIGHT + CELL_SIZE//2), 
                         CELL_SIZE//2)

        # Kiểm tra game over
        if self.game_over:
            font = pygame.font.SysFont('Arial', 36)
            text = font.render("Game Over - Press SPACE to restart", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, (SCREEN_HEIGHT + SCORE_HEIGHT)//2))
            screen.blit(text, text_rect)

        pygame.display.flip()

def main():
    game = SnakeGame()

    running = True
    while running:
        game.update()
        game.draw()

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_over:
                    game = SnakeGame()
                    game.generation += 1

        clock.tick(15)  # Điều chỉnh tốc độ game

    pygame.quit()

if __name__ == "__main__":
    main()
