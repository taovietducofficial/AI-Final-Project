"""
Cách thức hoạt động của thuật toán Simulated Annealing trong game Snake:

1. Khởi tạo:
- Vị trí ban đầu của rắn ở giữa màn hình
- Vị trí thức ăn ngẫu nhiên
- Nhiệt độ ban đầu T0 (thường 1000-10000)
- Tốc độ làm lạnh α (0.95-0.99)
- Nhiệt độ dừng Tmin (thường 0.1-1)
- Số bước lặp mỗi nhiệt độ L (50-100)

2. Trong mỗi bước:
- Tại nhiệt độ T:
  + Tạo trạng thái láng giềng bằng cách:
    * Chọn ngẫu nhiên một hướng di chuyển mới
    * Tính toán vị trí mới của đầu rắn
  + Tính ΔE = E(new) - E(current):
    * E = khoảng cách Manhattan tới thức ăn
    * Cộng thêm điểm phạt nếu đâm tường/thân
  + Chấp nhận trạng thái mới nếu:
    * ΔE < 0 (trạng thái tốt hơn)
    * Hoặc random() < exp(-ΔE/T) (xác suất Boltzmann)
  + Lặp lại L lần
- Giảm nhiệt độ: T = α * T
- Dừng khi T < Tmin

3. Ưu điểm:
- Có khả năng thoát khỏi cực trị địa phương
- Cân bằng giữa khám phá và khai thác
- Hội tụ tới giải pháp tốt
- Thích nghi với không gian tìm kiếm phức tạp

4. Nhược điểm:
- Hiệu quả phụ thuộc vào tham số (T0, α, L)
- Có thể mất nhiều thời gian để hội tụ
- Không đảm bảo tìm được giải pháp tối ưu
- Khó điều chỉnh hàm năng lượng phù hợp

5. Các tham số quan trọng:
- T0: Nhiệt độ ban đầu
  + Cao: khám phá nhiều, chậm hội tụ
  + Thấp: dễ kẹt cực trị địa phương
- α: Tốc độ làm lạnh
  + Gần 1: hội tụ chậm, kết quả tốt
  + Nhỏ hơn: hội tụ nhanh, kết quả kém
- L: Số bước lặp mỗi nhiệt độ
  + Lớn: khám phá kỹ, chậm
  + Nhỏ: nhanh nhưng dễ bỏ sót
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

# Lớp SnakeGame để quản lý trò chơi
class SnakeGame:
    def __init__(self):
        # Khởi tạo con rắn ở giữa màn hình
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
            self.snake.insert(0, new_head)  # Thêm đầu mới mà không xóa đuôi
            self.food = self.generate_food()  # Tạo thức ăn mới
            self.score += 1  # Tăng điểm
            if self.score > self.best_score:
                self.best_score = self.score  # Cập nhật điểm cao nhất
        else:
            self.snake = [new_head] + self.snake[:-1]  # Di chuyển bình thường

    # Kiểm tra va chạm
    def is_collision(self):
        head = self.snake[0]
        # Kiểm tra va chạm với thân hoặc tường
        return (head in self.snake[1:] or
                head[0] < 0 or head[1] < 0 or
                head[0] >= WIDTH or head[1] >= HEIGHT)

    # Tính khoảng cách Manhattan giữa hai điểm
    def compute_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # Thuật toán Simulated Annealing để chọn hướng di chuyển
    def choose_direction_simulated_annealing(self, temperature):
        head = self.snake[0]
        current_distance = self.compute_distance(head, self.food)

        best_direction = self.direction
        best_score = current_distance

        # Xem xét tất cả các hướng có thể
        for direction, (dx, dy) in MOVE_MAP.items():
            new_head = (head[0] + dx * CELL_SIZE, head[1] + dy * CELL_SIZE)
            # Bỏ qua các bước đi không hợp lệ
            if new_head in self.snake or new_head[0] < 0 or new_head[1] < 0 or \
               new_head[0] >= WIDTH or new_head[1] >= HEIGHT:
                continue

            new_distance = self.compute_distance(new_head, self.food)
            delta = new_distance - current_distance

            # Chấp nhận trạng thái tốt hơn hoặc xấu hơn với xác suất phụ thuộc vào nhiệt độ
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                best_direction = direction
                best_score = new_distance

        return best_direction


# Vòng lặp chính của game
def main():
    # Khởi tạo màn hình và các thành phần
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    game = SnakeGame()
    font = pygame.font.Font(None, 36)

    # Các tham số cho thuật toán Simulated Annealing
    initial_temperature = 100.0  # Nhiệt độ ban đầu
    cooling_rate = 0.99  # Tốc độ làm mát
    temperature = initial_temperature

    running = True
    while running:
        screen.fill(SCORE_BG)  # Vẽ nền cho khu vực điểm số
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))  # Vẽ nền cho khu vực chơi

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Chọn bước đi tiếp theo sử dụng Simulated Annealing
        game.direction = game.choose_direction_simulated_annealing(temperature)
        game.move_snake(game.direction)

        # Giảm nhiệt độ theo thời gian
        temperature = max(0.1, temperature * cooling_rate)

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
                # Vẽ mắt
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

        pygame.display.flip()  # Cập nhật màn hình
        clock.tick(10)  # Giới hạn FPS

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
