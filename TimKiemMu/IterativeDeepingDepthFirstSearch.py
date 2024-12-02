"""
Cách thức hoạt động của thuật toán Iterative Deepening Depth First Search trong game Snake:

1. Khái niệm:
- Là sự kết hợp giữa DFS và BFS
- Thực hiện DFS với độ sâu tăng dần
- Bắt đầu từ độ sâu 1, tăng dần lên đến khi tìm thấy
- Kết hợp ưu điểm của cả DFS và BFS

2. Cách hoạt động:
- Khởi tạo:
  + Độ sâu ban đầu d = 1
  + Stack chứa trạng thái hiện tại
  + Set lưu các trạng thái đã thăm
  
- Với mỗi độ sâu d:
  + Thực hiện DFS với giới hạn d:
    * Lấy trạng thái từ stack
    * Nếu độ sâu > d -> bỏ qua
    * Với mỗi hướng di chuyển:
      - Tính vị trí mới
      - Kiểm tra hợp lệ
      - Nếu chưa thăm -> đưa vào stack
      - Đánh dấu đã thăm
    * Nếu tìm thấy thức ăn -> trả về đường đi
  + Nếu không tìm thấy -> tăng d lên 1
  + Lặp lại cho đến khi tìm thấy hoặc hết không gian

3. Ưu điểm:
- Tìm được đường đi ngắn nhất
- Tiết kiệm bộ nhớ như DFS
- Tránh được vòng lặp vô hạn
- Phù hợp với không gian lớn

4. Nhược điểm:
- Phải duyệt lại các nút nhiều lần
- Tốc độ chậm hơn DFS và BFS
- Tốn thời gian với độ sâu lớn
- Khó xác định độ sâu tối đa

5. Cải tiến có thể:
- Lưu trữ kết quả các độ sâu trước
- Song song hóa các độ sâu
- Kết hợp với heuristic
- Sử dụng bộ nhớ cache
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên

# Các tham số cài đặt cho game
SCREEN_WIDTH = 800  # Chiều rộng màn hình game
SCREEN_HEIGHT = 600  # Chiều cao màn hình game
CELL_SIZE = 20  # Kích thước mỗi ô vuông trên màn hình
UP = (0, -1)  # Vector di chuyển lên
DOWN = (0, 1)  # Vector di chuyển xuống  
LEFT = (-1, 0)  # Vector di chuyển sang trái
RIGHT = (1, 0)  # Vector di chuyển sang phải

# Định nghĩa các màu sắc
WHITE = (255, 255, 255)  # Màu trắng
GREEN = (0, 255, 0)  # Màu xanh lá cho thân rắn
RED = (255, 0, 0)  # Màu đỏ cho thức ăn
BLACK = (0, 0, 0)  # Màu đen cho nền

# Khởi tạo pygame
pygame.init()

# Biến toàn cục để lưu điểm cao nhất và số thế hệ
HIGH_SCORE = 0  # Điểm cao nhất đạt được
GENERATION = 1  # Số thế hệ hiện tại

class SnakeGame:
    def __init__(self):
        # Khởi tạo màn hình game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Iterative Deepening DFS")
        
        # Khởi tạo vị trí ban đầu của rắn
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Danh sách các điểm của rắn
        self.direction = RIGHT  # Hướng di chuyển ban đầu
        self.food = self.random_food()  # Vị trí thức ăn ngẫu nhiên
        self.game_over = False  # Trạng thái game
        self.clock = pygame.time.Clock()  # Đồng hồ game
        self.score = 0  # Điểm số hiện tại

    def random_food(self):
        """Tạo vị trí ngẫu nhiên cho thức ăn, đảm bảo không trùng với thân rắn"""
        while True:
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:  # Kiểm tra không trùng với thân rắn
                return food_pos

    def draw_snake(self):
        """Vẽ rắn với thân và mắt"""
        # Vẽ thân rắn
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        
        # Vẽ mắt rắn
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn
        eye_radius = 3  # Bán kính mắt
        
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
        """Vẽ thức ăn dạng hình tròn màu đỏ"""
        food_x, food_y = self.food
        center_x = food_x + CELL_SIZE // 2
        center_y = food_y + CELL_SIZE // 2
        pygame.draw.circle(self.screen, RED, (center_x, center_y), CELL_SIZE // 2)

    def move_snake(self):
        """Di chuyển rắn theo hướng hiện tại"""
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)
        self.snake = [new_head] + self.snake[:-1]

    def check_collision(self):
        """Kiểm tra va chạm với tường, thân rắn và thức ăn"""
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
            self.food = self.random_food()  # Tạo thức ăn mới
            self.score += 1  # Tăng điểm

    def reset_game(self):
        """Reset game về trạng thái ban đầu"""
        global GENERATION
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = RIGHT
        self.food = self.random_food()
        GENERATION += 1
        self.score = 0

    def iterative_deepening_dfs(self, start, goal, max_depth):
        """Thuật toán Iterative Deepening DFS để tìm đường đi từ rắn đến thức ăn"""
        for depth_limit in range(max_depth):
            path = self.dfs_with_limit(start, goal, depth_limit)
            if path:
                return path
        return []

    def dfs_with_limit(self, start, goal, depth_limit):
        """DFS với giới hạn độ sâu để tìm đường đi"""
        stack = [(start, [], 0)]  # (vị trí hiện tại, đường đi, độ sâu)
        visited = set()  # Tập các vị trí đã thăm

        while stack:
            current_pos, path, depth = stack.pop()

            if depth > depth_limit:  # Nếu vượt quá độ sâu cho phép
                continue

            if current_pos == goal:  # Nếu đã đến đích
                return path

            if current_pos in visited:  # Nếu đã thăm vị trí này
                continue

            visited.add(current_pos)

            # Thử các hướng di chuyển có thể
            directions = [UP, DOWN, LEFT, RIGHT]
            for direction in directions:
                new_pos = (current_pos[0] + direction[0] * CELL_SIZE, current_pos[1] + direction[1] * CELL_SIZE)

                # Kiểm tra nước đi hợp lệ
                if (0 <= new_pos[0] < SCREEN_WIDTH and 
                    0 <= new_pos[1] < SCREEN_HEIGHT and 
                    new_pos not in self.snake[:-1]):
                    stack.append((new_pos, path + [direction], depth + 1))

        return []  # Không tìm thấy đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return
        
        # Tìm đường đi tới thức ăn
        path = self.iterative_deepening_dfs(self.snake[0], self.food, 50)

        if path:  # Nếu tìm được đường đi
            self.direction = path[0]  # Cập nhật hướng di chuyển
            self.move_snake()  # Di chuyển rắn
            self.check_collision()  # Kiểm tra va chạm
        else:  # Nếu không tìm được đường đi
            self.reset_game()  # Reset game

    def draw(self):
        """Vẽ toàn bộ game lên màn hình"""
        self.screen.fill(BLACK)  # Xóa màn hình
        self.draw_snake()  # Vẽ rắn
        self.draw_food()  # Vẽ thức ăn
        
        # Hiển thị thông tin game
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {HIGH_SCORE}', True, WHITE)
        gen_text = font.render(f'Generation: {GENERATION}', True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(gen_text, (10, 90))
        
        pygame.display.flip()  # Cập nhật màn hình

    def main(self):
        """Vòng lặp chính của game"""
        while not self.game_over:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            self.update()  # Cập nhật trạng thái game
            self.draw()  # Vẽ lại màn hình
            self.clock.tick(10)  # Giới hạn tốc độ game

        pygame.quit()  # Kết thúc pygame


# Khởi chạy game khi chạy trực tiếp file này
if __name__ == "__main__":
    game = SnakeGame()
    game.main()
