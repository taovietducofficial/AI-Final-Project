"""
Cách thức hoạt động của thuật toán Hill Climbing trong game Snake:

1. Khởi tạo:
- Vị trí ban đầu của rắn ở giữa màn hình
- Vị trí thức ăn ngẫu nhiên
- Hướng di chuyển ban đầu
- Hàm đánh giá f(state) dựa trên:
  + Khoảng cách Manhattan tới thức ăn
  + Độ an toàn của đường đi
  + Điểm số hiện tại
  + Số ô trống xung quanh đầu rắn

2. Trong mỗi bước:
- Tạo các trạng thái láng giềng bằng cách thử 4 hướng di chuyển
- Đánh giá từng trạng thái láng giềng:
  + Tính khoảng cách Manhattan tới thức ăn
  + Kiểm tra tính hợp lệ (không đâm tường/thân)
  + Tính điểm an toàn (số ô trống xung quanh)
  + Kết hợp các yếu tố thành điểm tổng

- Chọn trạng thái láng giềng tốt nhất:
  + Nếu tốt hơn trạng thái hiện tại -> di chuyển tới đó
  + Nếu không tốt hơn -> kẹt ở cực trị địa phương:
    * Thử ngẫu nhiên một hướng khác
    * Hoặc khởi tạo lại từ vị trí khác
    * Hoặc chấp nhận giải pháp hiện tại

3. Điều kiện dừng:
- Tìm được đường đi tới thức ăn
- Hoặc không còn trạng thái láng giềng hợp lệ
- Hoặc đạt số bước tối đa

4. Ưu điểm:
- Đơn giản, dễ cài đặt
- Tốc độ nhanh
- Tiêu tốn ít bộ nhớ
- Phù hợp với không gian tìm kiếm nhỏ

5. Nhược điểm:
- Dễ bị kẹt ở cực trị địa phương
- Không đảm bảo tìm được giải pháp tối ưu
- Phụ thuộc nhiều vào trạng thái ban đầu
- Khó xử lý khi không gian tìm kiếm lớn

6. Cải tiến có thể:
- Random-restart hill climbing
- Steepest ascent hill climbing  
- Stochastic hill climbing
- First-choice hill climbing
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên
import math  # Thư viện để tính toán

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
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']  # Các hướng có thể di chuyển
MOVE_MAP = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}  # Vector di chuyển tương ứng

# Lớp SnakeGame để quản lý trạng thái và logic của game
class SnakeGame:
    def __init__(self):
        # Khởi tạo vị trí ban đầu của rắn ở giữa màn hình
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
            # Đảm bảo thức ăn không xuất hiện trên thân rắn
            if food not in self.snake:
                return food

    # Phương thức di chuyển rắn
    def move_snake(self, direction):
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn
        move_x, move_y = MOVE_MAP[direction]  # Lấy vector di chuyển
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)  # Tính vị trí đầu mới
        
        # Kiểm tra nếu rắn ăn được thức ăn
        if new_head == self.food:
            self.snake.insert(0, new_head)  # Thêm đầu mới mà không xóa đuôi
            self.food = self.generate_food()  # Tạo thức ăn mới
            self.score += 1  # Tăng điểm
            if self.score > self.best_score:
                self.best_score = self.score
        else:
            # Di chuyển bình thường: thêm đầu mới và xóa đuôi cũ
            self.snake = [new_head] + self.snake[:-1]

    # Kiểm tra va chạm
    def is_collision(self):
        head = self.snake[0]
        # Va chạm với thân rắn hoặc tường
        return (head in self.snake[1:] or
                head[0] < 0 or head[1] < 0 or
                head[0] >= WIDTH or head[1] >= HEIGHT)

    # Tính khoảng cách Manhattan giữa hai điểm
    def compute_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # Thuật toán Hill Climbing để chọn hướng di chuyển tiếp theo
    def choose_direction_hill_climbing(self):
        head = self.snake[0]
        best_direction = None
        best_score = float('inf')  # Khởi tạo điểm tốt nhất là vô cùng

        # Kiểm tra tất cả các hướng có thể
        for direction, (dx, dy) in MOVE_MAP.items():
            new_head = (head[0] + dx * CELL_SIZE, head[1] + dy * CELL_SIZE)
            # Kiểm tra nước đi hợp lệ
            if new_head in self.snake or new_head[0] < 0 or new_head[1] < 0 or \
               new_head[0] >= WIDTH or new_head[1] >= HEIGHT:
                continue

            # Tính khoảng cách đến thức ăn
            distance = self.compute_distance(new_head, self.food)
            # Cập nhật hướng tốt nhất nếu tìm thấy khoảng cách ngắn hơn
            if distance < best_score:
                best_score = distance
                best_direction = direction

        # Nếu không có hướng hợp lệ, chọn ngẫu nhiên
        if best_direction is None:
            best_direction = random.choice(DIRECTIONS)

        return best_direction

# Hàm main để chạy game
def main():
    # Khởi tạo màn hình và các thành phần cần thiết
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    game = SnakeGame()
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        # Vẽ nền
        screen.fill(SCORE_BG)
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Sử dụng Hill Climbing để chọn hướng đi tiếp theo
        game.direction = game.choose_direction_hill_climbing()
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
                eye_radius = 3
                pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                pygame.draw.circle(screen, WHITE, (segment[0] + 3*CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
            else:  # Vẽ thân rắn
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Vẽ thức ăn với hiệu ứng nâng cao
        food_y = game.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Hiển thị điểm số
        score_text = font.render(f'Score: {game.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {game.best_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(10)  # Giới hạn FPS = 10

    # Chờ người dùng đóng cửa sổ
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()

# Chạy game khi file được thực thi trực tiếp
if __name__ == "__main__":
    main()
