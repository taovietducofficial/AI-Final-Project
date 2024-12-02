"""
Cách thức hoạt động của thuật toán Local Beam Search trong game Snake:

1. Khởi tạo:
- Tạo k trạng thái ban đầu ngẫu nhiên (k là beam width, thường từ 10-50)
- Mỗi trạng thái bao gồm:
  + Vị trí của rắn (danh sách các điểm)
  + Vị trí thức ăn (tọa độ x,y)
  + Hướng di chuyển hiện tại (UP/DOWN/LEFT/RIGHT)
  + Điểm số (độ dài rắn - 1)

2. Trong mỗi bước:
- Với mỗi trạng thái trong beam:
  + Tạo các trạng thái con bằng cách thử 4 hướng di chuyển có thể
  + Đánh giá các trạng thái con dựa trên hàm đánh giá:
    * Khoảng cách Manhattan tới thức ăn (càng gần càng tốt)
    * Độ an toàn của đường đi (số ô trống xung quanh đầu rắn)
    * Điểm số hiện tại (càng cao càng tốt)
    * Khả năng thoát hiểm (có đường đi thoát sau khi ăn)
  + Loại bỏ các trạng thái không hợp lệ (đâm tường/thân)
- Gộp tất cả trạng thái con lại
- Sắp xếp theo điểm đánh giá và chọn k trạng thái tốt nhất
- Lặp lại quá trình cho đến khi:
  + Tìm được đường đi tới thức ăn (khoảng cách = 0)
  + Hoặc đạt số bước tối đa (thường 100-200 bước)
  + Hoặc không còn trạng thái hợp lệ

3. Ưu điểm:
- Khám phá song song nhiều đường đi tiềm năng
- Giảm đáng kể khả năng bị kẹt ở cực trị địa phương
- Cân bằng tốt giữa khám phá (exploration) và khai thác (exploitation)
- Thích nghi tốt với không gian trạng thái lớn
- Có khả năng phục hồi khi gặp đường cụt

4. Nhược điểm:
- Tốn nhiều bộ nhớ để lưu và xử lý k trạng thái song song
- Chi phí tính toán cao do phải đánh giá nhiều trạng thái mỗi bước
- Hiệu quả phụ thuộc nhiều vào tham số k:
  + k nhỏ: dễ bị kẹt, ít khám phá
  + k lớn: tốn tài nguyên, chậm
- Cần thiết kế hàm đánh giá tốt và cân bằng
- Khó điều chỉnh các tham số cho tối ưu
"""



# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên
from collections import deque  # Thư viện để sử dụng hàng đợi hai đầu

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
DIRECTIONS = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# Lớp GameState để lưu trữ trạng thái game
class GameState:
    def __init__(self, snake, food, direction):
        self.snake = snake  # Danh sách các điểm của rắn
        self.food = food  # Vị trí thức ăn
        self.direction = direction  # Hướng di chuyển hiện tại
        self.score = len(snake) - 1  # Điểm số = độ dài rắn - 1

    # Phương thức tạo trạng thái tiếp theo dựa trên hành động
    def next_state(self, action):
        head_x, head_y = self.snake[0]  # Lấy vị trí đầu rắn
        move_x, move_y = DIRECTIONS[action]  # Lấy vector di chuyển
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)  # Tính vị trí đầu mới
        
        new_snake = [new_head] + self.snake[:-1]  # Tạo thân rắn mới
        if new_head == self.food:  # Nếu ăn được thức ăn
            new_snake.append(self.snake[-1])  # Thêm một đốt vào đuôi
        return GameState(new_snake, self.food, action)

    # Kiểm tra trạng thái có hợp lệ không
    def is_valid(self, width, height):
        head = self.snake[0]
        # Kiểm tra rắn trong màn hình và không đâm vào thân
        return (0 <= head[0] < width and 0 <= head[1] < height and
                len(self.snake) == len(set(self.snake)))

    # Hàm đánh giá khoảng cách đến thức ăn
    def heuristic(self):
        head = self.snake[0]
        food = self.food
        return abs(head[0] - food[0]) + abs(head[1] - food[1])  # Khoảng cách Manhattan

# Thuật toán Beam Search
def beam_search(game_state, width, height, beam_width=3, depth=10):
    beam = deque([game_state])  # Khởi tạo với trạng thái hiện tại

    # Lặp qua các độ sâu
    for _ in range(depth):
        candidates = []  # Danh sách các trạng thái ứng viên
        for state in beam:
            # Thử mọi hướng di chuyển có thể
            for action in DIRECTIONS.keys():
                next_state = state.next_state(action)
                if next_state.is_valid(width, height):
                    candidates.append(next_state)

        # Sắp xếp theo heuristic và giữ lại k trạng thái tốt nhất
        candidates.sort(key=lambda s: s.heuristic())
        beam = deque(candidates[:beam_width])

    # Trả về trạng thái tốt nhất
    return beam[0] if beam else None

# Hàm chính của game
def main():
    # Khởi tạo màn hình và các thông số
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Beam Search")

    # Font chữ cho hiển thị điểm
    font = pygame.font.Font(None, 36)
    
    # Điểm cao nhất
    high_score = 0

    # Khởi tạo rắn và thức ăn
    snake = [(WIDTH // 2, HEIGHT // 2)]  # Rắn bắt đầu ở giữa màn hình
    food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)

    game_state = GameState(snake, food, 'UP')
    running = True

    # Vòng lặp chính của game
    while running:
        # Vẽ nền
        screen.fill(SCORE_BG)
        pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Sử dụng Beam Search để quyết định bước đi tiếp theo
        next_state = beam_search(game_state, WIDTH, HEIGHT)
        if next_state:
            game_state = next_state
            high_score = max(high_score, game_state.score)
        else:
            print("Game Over!")
            running = False

        # Vẽ rắn với hiệu ứng nâng cao
        for i, segment in enumerate(game_state.snake):
            adjusted_y = segment[1] + SCORE_HEIGHT
            if i == 0:  # Vẽ đầu rắn
                pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                # Vẽ mắt rắn theo hướng di chuyển
                eye_size = 4
                if game_state.direction == 'RIGHT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game_state.direction == 'LEFT':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                elif game_state.direction == 'UP':
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + 5), eye_size)
                else:  # DOWN
                    pygame.draw.circle(screen, WHITE, (segment[0] + 5, adjusted_y + CELL_SIZE - 5), eye_size)
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE - 5, adjusted_y + CELL_SIZE - 5), eye_size)
            else:  # Vẽ thân rắn
                pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

        # Vẽ thức ăn
        food_y = game_state.food[1] + SCORE_HEIGHT
        pygame.draw.circle(screen, RED, (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
        pygame.draw.circle(screen, (200, 0, 0), (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)

        # Hiển thị điểm số
        score_text = font.render(f'Score: {game_state.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(10)  # Giới hạn FPS

    # Giữ cửa sổ mở sau khi game kết thúc
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

# Chạy game khi file được thực thi trực tiếp
if __name__ == "__main__":
    main()
