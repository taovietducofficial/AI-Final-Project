"""
Cách thức hoạt động của thuật toán Depth First Search trong game Snake:

1. Khái niệm:
- Là thuật toán tìm kiếm theo chiều sâu
- Khám phá càng sâu càng tốt trước khi quay lui
- Sử dụng stack để lưu các trạng thái cần duyệt
- Đánh dấu các trạng thái đã thăm

2. Cách hoạt động trong game Snake:
- Khởi tạo:
  + Stack chứa vị trí đầu rắn ban đầu
  + Set lưu các ô đã thăm
  + Mảng lưu đường đi tới thức ăn

- Trong mỗi bước:
  + Lấy vị trí hiện tại từ stack
  + Với mỗi hướng di chuyển có thể:
    * Tính vị trí mới của đầu rắn
    * Kiểm tra tính hợp lệ (không đâm tường/thân)
    * Nếu chưa thăm -> đưa vào stack
    * Đánh dấu đã thăm
    * Lưu lại đường đi
  + Nếu tìm thấy thức ăn -> trả về đường đi
  + Nếu không tìm được -> quay lui

3. Ưu điểm:
- Đảm bảo tìm được đường đi nếu tồn tại
- Tiêu tốn ít bộ nhớ hơn BFS
- Dễ cài đặt với đệ quy
- Phù hợp tìm đường trong mê cung

4. Nhược điểm:
- Không đảm bảo đường đi ngắn nhất
- Có thể bị kẹt trong nhánh sâu
- Không hiệu quả với không gian rộng
- Tốc độ chậm hơn BFS

5. Cải tiến có thể:
- Thêm giới hạn độ sâu
- Kết hợp với heuristic
- Song song hóa các nhánh tìm kiếm
- Tối ưu bộ nhớ với backtracking
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
HIGH_SCORE = 0
GENERATION = 1

# Lớp SnakeGame để quản lý trò chơi
class SnakeGame:
    def __init__(self):
        # Khởi tạo màn hình game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game with Depth First Search")
        
        # Khởi tạo vị trí ban đầu của rắn
        self.snake = [(100, 100), (80, 100), (60, 100)]  
        self.direction = RIGHT  # Hướng di chuyển ban đầu
        self.food = self.random_food()  # Tạo thức ăn đầu tiên
        self.game_over = False  # Trạng thái game
        self.clock = pygame.time.Clock()  # Đồng hồ để kiểm soát FPS
        self.score = 0  # Điểm số hiện tại

    def random_food(self):
        """Tạo vị trí ngẫu nhiên cho thức ăn"""
        while True:
            food_pos = (random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                    random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
            if food_pos not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                return food_pos

    def draw_snake(self):
        """Vẽ rắn và mắt rắn"""
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
        """Vẽ thức ăn dạng hình tròn"""
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
        """Kiểm tra va chạm của rắn"""
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
        """Reset lại game khi thua"""
        global GENERATION
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = RIGHT
        self.food = self.random_food()
        GENERATION += 1
        self.score = 0

    def dfs(self, start, goal):
        """Thuật toán DFS để tìm đường đi từ rắn đến thức ăn"""
        stack = [(start, [])]  # Stack lưu vị trí hiện tại và đường đi
        visited = set()  # Set lưu các vị trí đã thăm

        while stack:
            current_pos, path = stack.pop()

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
                    stack.append((new_pos, path + [direction]))

        return []  # Không tìm được đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return
        
        # Tìm đường đi từ rắn đến thức ăn
        path = self.dfs(self.snake[0], self.food)

        # Di chuyển rắn theo đường đi tìm được
        if path:
            self.direction = path[0]
            self.move_snake()
            self.check_collision()
        else:
            # Reset game nếu không tìm được đường đi
            self.reset_game()

    def draw(self):
        """Vẽ toàn bộ game lên màn hình"""
        self.screen.fill(BLACK)
        self.draw_snake()
        self.draw_food()
        
        # Hiển thị điểm và thông tin game
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
            self.clock.tick(10)  # Giới hạn FPS = 10

        pygame.quit()


# Chạy game khi file được thực thi trực tiếp
if __name__ == "__main__":
    game = SnakeGame()
    game.main()
