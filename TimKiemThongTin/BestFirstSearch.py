"""
Cách thức hoạt động của thuật toán Best First Search trong game Snake:

1. Khái niệm:
- Là thuật toán tìm kiếm theo heuristic
- Chọn nút có giá trị heuristic tốt nhất để mở rộng
- Sử dụng hàng đợi ưu tiên để lưu các trạng thái
- Không đảm bảo tìm được đường đi tối ưu

2. Cách hoạt động:
- Khởi tạo:
  + Hàng đợi ưu tiên chứa trạng thái ban đầu
  + Hàm heuristic đánh giá khoảng cách đến đích
  + Set lưu các trạng thái đã thăm
  + Dictionary lưu đường đi

- Trong mỗi bước:
  + Lấy trạng thái có heuristic tốt nhất từ hàng đợi
  + Với mỗi hướng di chuyển có thể:
    * Tính vị trí mới và giá trị heuristic
    * Kiểm tra tính hợp lệ
    * Nếu chưa thăm -> đưa vào hàng đợi
    * Đánh dấu đã thăm
  + Nếu tìm thấy thức ăn -> trả về đường đi
  + Nếu không tìm được -> tiếp tục

3. Ưu điểm:
- Tìm đường nhanh hơn tìm kiếm mù
- Tiết kiệm bộ nhớ hơn A*
- Dễ cài đặt và điều chỉnh heuristic
- Phù hợp khi không cần đường đi tối ưu

4. Nhược điểm:
- Không đảm bảo tìm được đường ngắn nhất
- Phụ thuộc nhiều vào hàm heuristic
- Có thể bị kẹt ở cực tiểu địa phương
- Không hiệu quả với không gian phức tạp

5. Cải tiến có thể:
- Kết hợp với chi phí thực (A*)
- Sử dụng nhiều heuristic khác nhau
- Thêm cơ chế thoát cực tiểu địa phương
- Song song hóa tính toán
"""


import pygame  # Thư viện để tạo game
import random  # Thư viện để tạo số ngẫu nhiên
from collections import deque  # Thư viện để sử dụng hàng đợi trong BFS

# Kích thước của màn hình game
SCREEN_WIDTH = 600  # Chiều rộng màn hình
SCREEN_HEIGHT = 600  # Chiều cao màn hình game
SCORE_HEIGHT = 50  # Chiều cao phần hiển thị điểm số
CELL_SIZE = 20  # Kích thước mỗi ô vuông trong game

# Định nghĩa các màu sắc sử dụng trong game
WHITE = (255, 255, 255)  # Màu trắng
GREEN = (0, 255, 0)  # Màu xanh lá
RED = (255, 0, 0)  # Màu đỏ
BLACK = (0, 0, 0)  # Màu đen
SCORE_BG = (50, 50, 50)  # Màu nền phần hiển thị điểm
SNAKE_HEAD = (0, 200, 0)  # Màu đầu rắn
SNAKE_BODY = (0, 255, 0)  # Màu thân rắn

# Định nghĩa các hướng di chuyển
UP = (0, -1)  # Di chuyển lên
DOWN = (0, 1)  # Di chuyển xuống
LEFT = (-1, 0)  # Di chuyển sang trái
RIGHT = (1, 0)  # Di chuyển sang phải

# Khởi tạo pygame
pygame.init()  # Khởi tạo tất cả các module pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + SCORE_HEIGHT))  # Tạo cửa sổ game
pygame.display.set_caption("Snake Game with BFS")  # Đặt tiêu đề cho cửa sổ game
clock = pygame.time.Clock()  # Đối tượng để kiểm soát FPS

# Lớp game Snake
class SnakeGame:
    def __init__(self):
        """Khởi tạo trò chơi"""
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]  # Vị trí ban đầu của rắn ở giữa màn hình
        self.direction = RIGHT  # Hướng di chuyển ban đầu
        self.food = None  # Vị trí của thức ăn
        self.generate_food()  # Tạo thức ăn đầu tiên
        self.game_over = False  # Trạng thái game
        self.score = 0  # Điểm số hiện tại
        self.best_score = 0  # Điểm số cao nhất
        self.generation = 1  # Số lần chơi

    def generate_food(self):
        """Tạo ra thức ăn ngẫu nhiên trên bàn cờ"""
        while True:
            food = (random.randrange(0, SCREEN_WIDTH, CELL_SIZE), 
                   random.randrange(0, SCREEN_HEIGHT, CELL_SIZE))
            if food not in self.snake:  # Đảm bảo thức ăn không xuất hiện trên thân rắn
                self.food = food
                break

    def move_snake(self):
        """Di chuyển rắn và kiểm tra va chạm"""
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn hiện tại
        new_head = (head_x + self.direction[0] * CELL_SIZE, head_y + self.direction[1] * CELL_SIZE)  # Tính vị trí đầu mới

        # Kiểm tra va chạm với chính mình hoặc tường
        if new_head in self.snake or not (0 <= new_head[0] < SCREEN_WIDTH and 0 <= new_head[1] < SCREEN_HEIGHT):
            if self.score > self.best_score:
                self.best_score = self.score
            self.game_over = True
            return False

        self.snake.insert(0, new_head)  # Thêm đầu mới vào rắn

        # Kiểm tra nếu rắn ăn thức ăn
        if new_head == self.food:
            self.score += 1  # Tăng điểm
            self.generate_food()  # Tạo thức ăn mới
        else:
            self.snake.pop()  # Xóa đuôi rắn nếu không ăn thức ăn

        return True

    def bfs(self):
        """
        Hàm thực hiện thuật toán Best First Search để tìm đường đi ngắn nhất từ đầu rắn đến thức ăn.
        
        Cách hoạt động:
        1. Khởi tạo:
           - Điểm bắt đầu là đầu rắn
           - Điểm đích là vị trí thức ăn
           - Hàng đợi queue lưu các vị trí cần xét và đường đi tới đó
           - Set visited lưu các ô đã thăm
        
        2. Lặp cho đến khi tìm được đường đi hoặc hết khả năng:
           - Lấy vị trí hiện tại và đường đi từ queue
           - Nếu đến đích thì trả về đường đi
           - Thử các hướng di chuyển có thể (UP/DOWN/LEFT/RIGHT)
           - Thêm các vị trí hợp lệ vào queue và visited
        
        3. Trả về:
           - Danh sách các hướng đi nếu tìm thấy đường
           - Danh sách rỗng nếu không tìm được đường đi
        """
        start = self.snake[0]  # Điểm bắt đầu là đầu rắn
        goal = self.food  # Điểm đích là thức ăn

        directions = [UP, DOWN, LEFT, RIGHT]  # Các hướng có thể di chuyển
        queue = deque([(start, [])])  # Hàng đợi chứa vị trí hiện tại và đường đi
        visited = set()  # Tập hợp các ô đã thăm
        visited.add(start)

        while queue:
            current, path = queue.popleft()  # Lấy vị trí và đường đi hiện tại

            if current == goal:  # Nếu đến đích
                return path  # Trả về đường đi

            # Thử tất cả các hướng có thể
            for direction in directions:
                new_pos = (current[0] + direction[0] * CELL_SIZE, current[1] + direction[1] * CELL_SIZE)
                # Kiểm tra điều kiện hợp lệ
                if 0 <= new_pos[0] < SCREEN_WIDTH and 0 <= new_pos[1] < SCREEN_HEIGHT and new_pos not in visited and new_pos not in self.snake:
                    queue.append((new_pos, path + [direction]))
                    visited.add(new_pos)

        return []  # Trả về rỗng nếu không tìm thấy đường đi

    def update(self):
        """Cập nhật trạng thái game"""
        if self.game_over:
            return

        path = self.bfs()  # Tìm đường đi đến thức ăn

        if path:
            self.direction = path[0]  # Đi theo hướng đầu tiên tìm được

        if not self.move_snake():  # Di chuyển rắn
            self.game_over = True

    def draw(self):
        """Vẽ game lên màn hình"""
        # Vẽ phần hiển thị điểm số
        screen.fill(SCORE_BG, (0, 0, SCREEN_WIDTH, SCORE_HEIGHT))
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        best_text = font.render(f'Best: {self.best_score}', True, WHITE)
        gen_text = font.render(f'Generation: {self.generation}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(best_text, (200, 10))
        screen.blit(gen_text, (400, 10))

        # Vẽ nền game
        screen.fill(BLACK, (0, SCORE_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Vẽ rắn
        for i, segment in enumerate(self.snake):
            if i == 0:  # Vẽ đầu rắn
                pygame.draw.rect(screen, SNAKE_HEAD, 
                               (segment[0], segment[1] + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))
                # Vẽ mắt rắn
                eye_radius = 3
                pygame.draw.circle(screen, WHITE, 
                                 (segment[0] + CELL_SIZE//4, segment[1] + SCORE_HEIGHT + CELL_SIZE//3), 
                                 eye_radius)
                pygame.draw.circle(screen, WHITE, 
                                 (segment[0] + 3*CELL_SIZE//4, segment[1] + SCORE_HEIGHT + CELL_SIZE//3), 
                                 eye_radius)
            else:  # Vẽ thân rắn
                pygame.draw.rect(screen, SNAKE_BODY, 
                               (segment[0], segment[1] + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))

        # Vẽ thức ăn
        pygame.draw.circle(screen, RED, 
                         (self.food[0] + CELL_SIZE//2, self.food[1] + SCORE_HEIGHT + CELL_SIZE//2), 
                         CELL_SIZE//2)

        # Hiển thị thông báo game over
        if self.game_over:
            font = pygame.font.SysFont('Arial', 36)
            text = font.render("Game Over - Press SPACE to restart", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, (SCREEN_HEIGHT + SCORE_HEIGHT)//2))
            screen.blit(text, text_rect)

        pygame.display.flip()  # Cập nhật toàn bộ màn hình

def main():
    """Hàm chính điều khiển game"""
    game = SnakeGame()  # Tạo instance game mới

    running = True
    while running:
        game.update()  # Cập nhật trạng thái game
        game.draw()  # Vẽ game

        # Xử lý các sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Nếu nhấn nút đóng cửa sổ
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_over:  # Nếu nhấn space khi game over
                    game = SnakeGame()  # Tạo game mới
                    game.generation += 1  # Tăng số lần chơi

        clock.tick(15)  # Giới hạn FPS là 15

    pygame.quit()  # Đóng pygame

if __name__ == "__main__":
    main()
