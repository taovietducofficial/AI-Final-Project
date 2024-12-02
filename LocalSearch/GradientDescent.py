"""
Cách thức hoạt động của thuật toán Gradient Descent trong game Snake:

1. Khởi tạo:
- Vị trí ban đầu của rắn ở giữa màn hình
- Vị trí thức ăn ngẫu nhiên
- Hàm mục tiêu f(x,y) = khoảng cách Manhattan từ đầu rắn đến thức ăn
- Learning rate α (tốc độ học, thường 0.1-0.5)

2. Trong mỗi bước:
- Tính gradient của hàm mục tiêu tại vị trí hiện tại:
  ∇f = (∂f/∂x, ∂f/∂y)
  = (sign(food_x - head_x), sign(food_y - head_y))

- Cập nhật vị trí theo gradient âm:
  x_new = x - α * ∂f/∂x
  y_new = y - α * ∂f/∂y

- Chọn hướng di chuyển dựa trên vector (x_new - x, y_new - y):
  + Nếu |x_new - x| > |y_new - y|:
    * Nếu x_new > x: RIGHT
    * Ngược lại: LEFT
  + Ngược lại:
    * Nếu y_new > y: DOWN
    * Ngược lại: UP

- Kiểm tra tính hợp lệ của hướng di chuyển:
  + Không đâm vào tường
  + Không đâm vào thân rắn
  + Nếu không hợp lệ, thử các hướng khác

3. Điều kiện dừng:
- Đến được thức ăn (f(x,y) = 0)
- Hoặc không tìm được hướng di chuyển hợp lệ
- Hoặc đạt số bước tối đa

4. Ưu điểm:
- Đơn giản, dễ cài đặt
- Hội tụ nhanh khi gần mục tiêu
- Tiêu tốn ít bộ nhớ

5. Nhược điểm:
- Dễ bị kẹt ở cực trị địa phương
- Hiệu quả phụ thuộc vào learning rate
- Khó tránh chướng ngại vật phức tạp
- Không tối ưu cho không gian rời rạc
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import math  # Thư viện để tính toán
import random  # Thư viện để tạo số ngẫu nhiên

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 400, 400  # Kích thước màn hình chơi game
CELL_SIZE = 20  # Kích thước mỗi ô vuông
SCORE_HEIGHT = 100  # Chiều cao khu vực hiển thị điểm

# Định nghĩa các màu sắc sử dụng trong game
BLACK = (0, 0, 0)  # Màu đen cho nền
WHITE = (255, 255, 255)  # Màu trắng
GREEN = (0, 255, 0)  # Màu xanh lá
RED = (255, 0, 0)  # Màu đỏ cho thức ăn
SNAKE_HEAD = (0, 200, 0)  # Màu xanh đậm cho đầu rắn
SNAKE_BODY = (50, 255, 50)  # Màu xanh nhạt cho thân rắn
SNAKE_BORDER = (0, 100, 0)  # Màu viền rắn
SCORE_BG = (50, 50, 50)  # Màu nền khu vực hiển thị điểm

# Định nghĩa các hướng di chuyển
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']  # Danh sách các hướng có thể di chuyển
MOVE_MAP = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}  # Vector di chuyển tương ứng với mỗi hướng

# Lớp SnakeGame để quản lý trò chơi
class SnakeGame:
    def __init__(self):
        # Khởi tạo rắn ở giữa màn hình
        self.snake = [(WIDTH // 2, HEIGHT // 2)]  
        self.food = self.generate_food()  # Tạo thức ăn đầu tiên
        self.direction = 'UP'  # Hướng di chuyển ban đầu
        self.score = 0  # Điểm số hiện tại
        self.best_score = 0  # Điểm số cao nhất

    # Phương thức tạo thức ăn mới
    def generate_food(self):
        while True:
            # Tạo vị trí ngẫu nhiên cho thức ăn
            food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                   random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                return food

    # Phương thức di chuyển rắn
    def move_snake(self, direction):
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn
        move_x, move_y = MOVE_MAP[direction]  # Lấy vector di chuyển
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)  # Tính vị trí đầu mới
        
        # Kiểm tra nếu rắn ăn được thức ăn
        if new_head == self.food:
            self.snake.insert(0, new_head)  # Thêm đầu mới
            self.food = self.generate_food()  # Tạo thức ăn mới
            self.score += 1  # Tăng điểm
            if self.score > self.best_score:
                self.best_score = self.score
        else:
            self.snake = [new_head] + self.snake[:-1]  # Di chuyển rắn bình thường

    # Kiểm tra va chạm
    def is_collision(self):
        head = self.snake[0]
        return (head in self.snake[1:] or  # Va chạm với thân
                head[0] < 0 or head[1] < 0 or  # Va chạm với biên trái/trên
                head[0] >= WIDTH or head[1] >= HEIGHT)  # Va chạm với biên phải/dưới

    # Tính gradient (độ dốc) để xác định hướng di chuyển tốt nhất
    def compute_gradient(self):
        head_x, head_y = self.snake[0]  # Vị trí đầu rắn
        food_x, food_y = self.food  # Vị trí thức ăn

        # Tính đạo hàm riêng theo x và y
        dx = food_x - head_x
        dy = food_y - head_y

        # Chuẩn hóa gradient
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude == 0:
            return 0, 0
        return dx / magnitude, dy / magnitude

    # Chọn hướng di chuyển dựa trên gradient descent
    def choose_direction(self):
        gradient_x, gradient_y = self.compute_gradient()  # Tính gradient
        candidates = []  # Danh sách các hướng có thể di chuyển

        # Đánh giá từng hướng
        for direction, (dx, dy) in MOVE_MAP.items():
            # Mô phỏng vị trí tiếp theo
            head_x, head_y = self.snake[0]
            next_x = head_x + dx * CELL_SIZE
            next_y = head_y + dy * CELL_SIZE
            
            # Bỏ qua nếu sẽ gây va chạm
            if (next_x, next_y) in self.snake[1:] or \
               next_x < 0 or next_x >= WIDTH or \
               next_y < 0 or next_y >= HEIGHT:
                continue
                
            score = gradient_x * dx + gradient_y * dy  # Tích vô hướng
            candidates.append((score, direction))

        if not candidates:  # Nếu không có hướng an toàn, chọn ngẫu nhiên
            return random.choice(DIRECTIONS)
            
        # Chọn hướng có điểm cao nhất
        return max(candidates, key=lambda x: x[0])[1]

# Vòng lặp chính của game
def main():
    # Khởi tạo màn hình và các thành phần
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Gradient Descent")
    font = pygame.font.Font(None, 36)
    game = SnakeGame()

    running = True
    while running:
        # Vẽ khu vực hiển thị điểm
        screen.fill(SCORE_BG)
        # Vẽ khu vực chơi game
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Chọn hướng di chuyển tiếp theo bằng Gradient Descent
        game.direction = game.choose_direction()
        game.move_snake(game.direction)

        # Kiểm tra va chạm
        if game.is_collision():
            print(f"Game Over! Score: {game.score}")
            running = False

        # Vẽ rắn với hiệu ứng nâng cao
        for i, segment in enumerate(game.snake):
            adjusted_y = segment[1] + SCORE_HEIGHT
            if i == 0:  # Vẽ đầu rắn
                pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                # Vẽ mắt rắn
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
            else:  # Vẽ thân rắn
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Vẽ thức ăn với hiệu ứng nâng cao
        food_y = game.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Hiển thị điểm số
        score_text = font.render(f'Score: {game.score}', True, WHITE)
        best_score_text = font.render(f'Best Score: {game.best_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (WIDTH - best_score_text.get_width() - 10, 10))

        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(10)  # Giới hạn FPS

    # Giữ cửa sổ mở sau khi game kết thúc
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()

# Chạy game khi chạy trực tiếp file này
if __name__ == "__main__":
    main()
