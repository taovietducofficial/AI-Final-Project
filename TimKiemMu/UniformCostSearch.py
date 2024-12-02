"""
Cách thức hoạt động của thuật toán Uniform Cost Search trong game Snake:

1. Khái niệm:
- Là thuật toán tìm kiếm theo chi phí đồng nhất
- Mở rộng nút có chi phí thấp nhất trước
- Sử dụng hàng đợi ưu tiên để lưu các trạng thái
- Đảm bảo tìm được đường đi tối ưu

2. Cách hoạt động:
- Khởi tạo:
  + Hàng đợi ưu tiên chứa trạng thái ban đầu
  + Chi phí ban đầu = 0
  + Set lưu các trạng thái đã thăm
  + Dictionary lưu chi phí tới mỗi trạng thái

- Trong mỗi bước:
  + Lấy trạng thái có chi phí nhỏ nhất từ hàng đợi
  + Với mỗi hướng di chuyển có thể:
    * Tính vị trí mới và chi phí mới
    * Kiểm tra tính hợp lệ
    * Nếu chi phí mới tốt hơn -> cập nhật
    * Đưa vào hàng đợi ưu tiên
  + Nếu tìm thấy thức ăn -> trả về đường đi
  + Nếu không tìm được -> tiếp tục

3. Ưu điểm:
- Đảm bảo tìm được đường đi tối ưu
- Phù hợp với không gian có chi phí khác nhau
- Hiệu quả khi chi phí đường đi quan trọng
- Dễ mở rộng với các heuristic

4. Nhược điểm:
- Tốn nhiều bộ nhớ cho hàng đợi ưu tiên
- Chậm hơn BFS với chi phí đồng nhất
- Phức tạp trong cài đặt
- Không hiệu quả với không gian lớn

5. Cải tiến có thể:
- Kết hợp với heuristic (A*)
- Tối ưu hóa cấu trúc dữ liệu
- Song song hóa tính toán
- Sử dụng bộ nhớ cache
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên
import heapq   # Thư viện để sử dụng hàng đợi ưu tiên

# Các tham số cài đặt cho game
SCREEN_WIDTH = 800  # Chiều rộng màn hình game
SCREEN_HEIGHT = 600  # Chiều cao màn hình game
CELL_SIZE = 20  # Kích thước mỗi ô vuông trong game
# Định nghĩa các hướng di chuyển
UP = (0, -1)  # Di chuyển lên trên
DOWN = (0, 1)  # Di chuyển xuống dưới
LEFT = (-1, 0)  # Di chuyển sang trái 
RIGHT = (1, 0)  # Di chuyển sang phải

# Định nghĩa các màu sắc sử dụng trong game
WHITE = (255, 255, 255)  # Màu trắng
GREEN = (0, 255, 0)  # Màu xanh lá cho thân rắn
RED = (255, 0, 0)  # Màu đỏ cho thức ăn
BLACK = (0, 0, 0)  # Màu đen cho nền

# Khởi tạo pygame
pygame.init()


class SnakeGame:
    def __init__(self):
        # Khởi tạo màn hình game và các thuộc tính ban đầu
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Uniform Cost Search")
        
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Vị trí ban đầu của rắn
        self.direction = RIGHT  # Hướng di chuyển ban đầu
        self.food = self.random_food()  # Vị trí thức ăn đầu tiên
        self.game_over = False  # Trạng thái game
        self.clock = pygame.time.Clock()  # Đồng hồ để kiểm soát FPS
        self.high_score = 0  # Điểm cao nhất
        self.generation = 1  # Số thế hệ hiện tại
        self.score = 0  # Điểm số hiện tại

    def random_food(self):
        """Tạo vị trí ngẫu nhiên cho thức ăn, đảm bảo không trùng với thân rắn"""
        while True:
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:
                return food_pos

    def draw_snake(self):
        """Vẽ rắn và mắt rắn"""
        # Vẽ thân rắn
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Vẽ mắt rắn khi rắn còn sống
        if not self.game_over:
            head = self.snake[0]
            eye_size = 4
            # Vẽ mắt trái và phải
            eye_left = (head[0] + 5, head[1] + 5)
            pygame.draw.circle(self.screen, WHITE, eye_left, eye_size)
            eye_right = (head[0] + 15, head[1] + 5)
            pygame.draw.circle(self.screen, WHITE, eye_right, eye_size)

    def draw_food(self):
        """Vẽ thức ăn dưới dạng hình tròn màu đỏ"""
        food_center = (self.food[0] + CELL_SIZE//2, self.food[1] + CELL_SIZE//2)
        pygame.draw.circle(self.screen, RED, food_center, CELL_SIZE//2)

    def move_snake(self):
        """Di chuyển rắn theo hướng hiện tại và xử lý xuyên tường"""
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)
        
        # Cho phép rắn xuyên qua tường
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)
        self.snake = [new_head] + self.snake[:-1]

    def check_collision(self):
        """Kiểm tra va chạm với thân rắn và thức ăn"""
        head = self.snake[0]
        # Kiểm tra va chạm với thân
        if head in self.snake[1:]:
            if self.score > self.high_score:
                self.high_score = self.score
            self.generation += 1
            self.reset_game()
        # Kiểm tra ăn thức ăn
        if head == self.food:
            self.snake.append(self.snake[-1])
            self.food = self.random_food()
            self.score += 1

    def reset_game(self):
        """Khởi tạo lại game khi thua"""
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = RIGHT
        self.food = self.random_food()
        self.score = 0

    def uniform_cost_search(self, start, goal):
        """Thuật toán Uniform Cost Search để tìm đường đi tối ưu từ rắn đến thức ăn"""
        pq = []  # Hàng đợi ưu tiên
        heapq.heappush(pq, (0, start, []))  # (chi phí, vị trí hiện tại, đường đi)
        visited = set()  # Tập các điểm đã thăm

        while pq:
            cost, current_pos, path = heapq.heappop(pq)

            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Nếu tìm thấy thức ăn
            if current_pos == goal:
                return path

            # Thử tất cả các hướng di chuyển có thể
            directions = [UP, DOWN, LEFT, RIGHT]
            for direction in directions:
                new_pos = (
                    (current_pos[0] + direction[0] * CELL_SIZE) % SCREEN_WIDTH,
                    (current_pos[1] + direction[1] * CELL_SIZE) % SCREEN_HEIGHT
                )

                # Chỉ di chuyển đến vị trí chưa thăm và không đâm vào thân rắn
                if new_pos not in visited and new_pos not in self.snake[1:]:
                    heapq.heappush(pq, (cost + 1, new_pos, path + [direction]))

        return []  # Không tìm thấy đường đi

    def update(self):
        """Cập nhật trạng thái game theo thuật toán UCS"""
        # Tìm đường đi từ đầu rắn đến thức ăn
        path = self.uniform_cost_search(self.snake[0], self.food)

        # Nếu tìm thấy đường đi, di chuyển theo hướng đầu tiên
        if path:
            self.direction = path[0]
            self.move_snake()
            self.check_collision()

    def draw(self):
        """Vẽ toàn bộ game và hiển thị thông tin"""
        self.screen.fill(BLACK)
        self.draw_snake()
        self.draw_food()
        
        # Hiển thị điểm số và thế hệ
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
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Cập nhật và vẽ game
            self.update()
            self.draw()
            self.clock.tick(10)  # Giới hạn FPS = 10

        pygame.quit()


# Khởi chạy game khi chạy trực tiếp file này
if __name__ == "__main__":
    game = SnakeGame()
    game.main()
