"""
Cách thức hoạt động của thuật toán Depth Limited Search trong game Snake:

1. Khái niệm:
- Là phiên bản cải tiến của DFS với giới hạn độ sâu
- Tránh bị kẹt trong nhánh sâu vô hạn
- Phù hợp khi biết giới hạn độ sâu cần tìm
- Sử dụng stack và độ sâu tối đa

2. Cách hoạt động:
- Khởi tạo:
  + Stack chứa trạng thái ban đầu
  + Độ sâu tối đa L (thường 10-20)
  + Set lưu các trạng thái đã thăm
  
- Trong mỗi bước:
  + Lấy trạng thái từ stack
  + Nếu độ sâu > L -> bỏ qua
  + Với mỗi hướng di chuyển:
    * Tính vị trí mới
    * Kiểm tra hợp lệ
    * Nếu chưa thăm -> đưa vào stack
    * Đánh dấu đã thăm
  + Nếu tìm thấy thức ăn -> trả về đường đi
  + Nếu không tìm được -> quay lui

3. Ưu điểm:
- Tránh được vòng lặp vô hạn
- Tiết kiệm bộ nhớ và thời gian
- Dễ điều chỉnh độ sâu tìm kiếm
- Phù hợp với không gian có độ sâu vừa phải

4. Nhược điểm:
- Có thể bỏ sót giải pháp ngoài độ sâu L
- Không đảm bảo tìm được đường ngắn nhất
- Hiệu quả phụ thuộc vào L
- Vẫn có thể chậm với L lớn

5. Cải tiến có thể:
- Kết hợp với heuristic
- Tăng giảm L động
- Song song hóa các nhánh
- Sử dụng bộ nhớ cache
"""

# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên

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
GREEN = (0, 255, 0)  # Màu xanh lá
RED = (255, 0, 0)  # Màu đỏ
BLACK = (0, 0, 0)  # Màu đen

# Khởi tạo pygame
pygame.init()

# Biến toàn cục để lưu điểm cao nhất và số thế hệ
HIGH_SCORE = 0  # Điểm cao nhất đạt được
GENERATION = 1  # Số thế hệ hiện tại

# Lớp chính để quản lý game
class SnakeGame:
    def __init__(self):
        # Khởi tạo màn hình game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Depth Limited Search")
        
        # Khởi tạo vị trí ban đầu của rắn
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Danh sách các phần của rắn
        self.direction = RIGHT  # Hướng di chuyển ban đầu
        self.food = self.random_food()  # Vị trí thức ăn
        self.game_over = False  # Trạng thái game
        self.clock = pygame.time.Clock()  # Đồng hồ để kiểm soát tốc độ game
        self.score = 0  # Điểm số hiện tại

    def random_food(self):
        """Tạo vị trí ngẫu nhiên cho thức ăn"""
        while True:
            # Tạo tọa độ ngẫu nhiên trong phạm vi màn hình
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                return food_pos

    def draw_snake(self):
        """Vẽ rắn lên màn hình"""
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
            
        # Vẽ hai mắt
        pygame.draw.circle(self.screen, WHITE, left_eye, eye_radius)
        pygame.draw.circle(self.screen, WHITE, right_eye, eye_radius)

    def draw_food(self):
        """Vẽ thức ăn lên màn hình"""
        food_x, food_y = self.food
        center_x = food_x + CELL_SIZE // 2
        center_y = food_y + CELL_SIZE // 2
        pygame.draw.circle(self.screen, RED, (center_x, center_y), CELL_SIZE // 2)

    def move_snake(self):
        """Di chuyển rắn"""
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn
        # Tính toán vị trí mới cho đầu rắn
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)
        self.snake = [new_head] + self.snake[:-1]  # Cập nhật vị trí rắn

    def check_collision(self):
        """Kiểm tra va chạm"""
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
        """Reset lại game khi thua"""
        global GENERATION
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Reset vị trí rắn
        self.direction = RIGHT  # Reset hướng di chuyển
        self.food = self.random_food()  # Tạo thức ăn mới
        GENERATION += 1  # Tăng số thế hệ
        self.score = 0  # Reset điểm số

    def depth_limited_search(self, start, goal, depth_limit):
        """Thuật toán Depth Limited Search để tìm đường đi đến thức ăn"""
        stack = [(start, [], 0)]  # (vị trí hiện tại, đường đi, độ sâu)
        visited = set()  # Tập các vị trí đã thăm

        while stack:
            current_pos, path, depth = stack.pop()

            # Nếu đạt đến độ sâu giới hạn thì bỏ qua
            if depth > depth_limit:
                continue

            # Nếu đã đến đích
            if current_pos == goal:
                return path

            visited.add(current_pos)

            # Thử các hướng di chuyển có thể
            directions = [UP, DOWN, LEFT, RIGHT]
            for direction in directions:
                new_pos = (current_pos[0] + direction[0] * CELL_SIZE, current_pos[1] + direction[1] * CELL_SIZE)

                # Kiểm tra nước đi hợp lệ
                if 0 <= new_pos[0] < SCREEN_WIDTH and 0 <= new_pos[1] < SCREEN_HEIGHT and new_pos not in visited and new_pos not in self.snake:
                    stack.append((new_pos, path + [direction], depth + 1))

        return []  # Trả về rỗng nếu không tìm được đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return
        
        # Tìm đường đi từ rắn đến thức ăn
        path = self.depth_limited_search(self.snake[0], self.food, 20)

        # Di chuyển rắn theo đường đi tìm được
        if path:
            self.direction = path[0]  # Lấy bước đi đầu tiên
            self.move_snake()  # Di chuyển rắn
            self.check_collision()  # Kiểm tra va chạm
        else:
            # Nếu không tìm được đường đi, reset game
            self.reset_game()

    def draw(self):
        """Vẽ toàn bộ game lên màn hình"""
        self.screen.fill(BLACK)  # Xóa màn hình
        self.draw_snake()  # Vẽ rắn
        self.draw_food()  # Vẽ thức ăn
        
        # Hiển thị thông tin điểm và generation
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
            # Xử lý các sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            self.update()  # Cập nhật trạng thái game
            self.draw()  # Vẽ lại màn hình
            self.clock.tick(10)  # Giới hạn tốc độ game

        pygame.quit()  # Thoát pygame khi kết thúc


# Chạy game khi file được thực thi trực tiếp
if __name__ == "__main__":
    game = SnakeGame()
    game.main()
