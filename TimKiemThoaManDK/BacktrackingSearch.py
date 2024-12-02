"""
Cách thức hoạt động của thuật toán Backtracking Search trong game Snake:

1. Khái niệm:
- Là thuật toán tìm kiếm quay lui
- Thử từng khả năng và quay lui khi không thỏa mãn
- Sử dụng đệ quy để thực hiện quay lui
- Đánh dấu và bỏ đánh dấu các trạng thái đã thử

2. Cách hoạt động:
- Khởi tạo:
  + Vị trí ban đầu là đầu rắn
  + Set lưu các ô đã thăm
  + List lưu đường đi tìm được
  
- Trong mỗi bước:
  + Kiểm tra nếu đã đến đích -> thành công
  + Với mỗi hướng di chuyển có thể:
    * Tính vị trí mới
    * Kiểm tra tính hợp lệ
    * Nếu hợp lệ:
      - Đánh dấu đã thăm
      - Thử đi tiếp (đệ quy)
      - Nếu thất bại -> bỏ đánh dấu và thử hướng khác
  + Nếu không có hướng nào đi được -> quay lui

3. Ưu điểm:
- Đảm bảo tìm được đường đi nếu tồn tại
- Tiết kiệm bộ nhớ
- Dễ cài đặt với đệ quy
- Phù hợp với bài toán có ràng buộc

4. Nhược điểm:
- Thời gian chạy có thể rất lâu
- Không đảm bảo đường đi ngắn nhất
- Dễ bị treo với dữ liệu lớn
- Tốc độ phụ thuộc thứ tự thử nghiệm

5. Cải tiến có thể:
- Thêm heuristic để ưu tiên hướng đi
- Giới hạn độ sâu đệ quy
- Lưu trữ các trạng thái đã thử
- Song song hóa các nhánh tìm kiếm
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import sys  # Thư viện để thoát chương trình
import random  # Thư viện để tạo số ngẫu nhiên

# Khởi tạo Pygame
pygame.init()

# Kích thước ô và màn hình
CELL_SIZE = 40  # Kích thước mỗi ô là 40 pixel
GRID_SIZE = 15  # Kích thước lưới 15x15 ô
SCREEN_SIZE = CELL_SIZE * GRID_SIZE  # Kích thước màn hình = 40 * 15 = 600 pixel
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))  # Tạo cửa sổ game
pygame.display.set_caption("Snake Game with Backtracking")  # Đặt tiêu đề cửa sổ
clock = pygame.time.Clock()  # Đối tượng để kiểm soát FPS

# Định nghĩa các màu sắc sử dụng trong game
BLACK = (0, 0, 0)  # Màu đen cho nền
WHITE = (255, 255, 255)  # Màu trắng cho lưới
GREEN = (0, 255, 0)  # Màu xanh lá cho rắn
RED = (255, 0, 0)  # Màu đỏ cho thức ăn
BLUE = (0, 0, 255)  # Màu xanh dương cho đường đi dự đoán

# Định nghĩa các hướng di chuyển có thể
DIRECTIONS = {
    "UP": (0, -1),     # Di chuyển lên: y giảm 1
    "DOWN": (0, 1),    # Di chuyển xuống: y tăng 1  
    "LEFT": (-1, 0),   # Di chuyển trái: x giảm 1
    "RIGHT": (1, 0)    # Di chuyển phải: x tăng 1
}

# Hàm tìm đường với thuật toán Backtracking
def find_path(snake, food, visited, path):
    """
    Tìm đường đi từ đầu rắn đến thức ăn sử dụng thuật toán Backtracking
    
    Args:
        snake: List các tọa độ phần thân rắn
        food: Tọa độ thức ăn
        visited: Set các ô đã thăm
        path: List lưu đường đi tìm được
    
    Returns:
        True nếu tìm được đường đi, False nếu không tìm được
    """
    head = snake[-1]  # Lấy vị trí đầu rắn
    if head == food:  # Nếu đã đến thức ăn
        return True

    # Sắp xếp các hướng theo khoảng cách Manhattan đến thức ăn
    directions = list(DIRECTIONS.values())
    directions.sort(key=lambda d: abs(head[0] + d[0] - food[0]) + abs(head[1] + d[1] - food[1]))

    # Thử từng hướng di chuyển
    for direction in directions:
        next_cell = (head[0] + direction[0], head[1] + direction[1])  # Tính ô tiếp theo

        # Kiểm tra ô tiếp theo có hợp lệ không
        if (
            0 <= next_cell[0] < GRID_SIZE  # Trong phạm vi x
            and 0 <= next_cell[1] < GRID_SIZE  # Trong phạm vi y
            and next_cell not in visited  # Chưa thăm
            and next_cell not in snake[:-1]  # Không đâm vào thân rắn
        ):
            visited.add(next_cell)  # Đánh dấu đã thăm
            path.append(next_cell)  # Thêm vào đường đi

            # Đệ quy tìm đường từ ô mới
            if find_path(snake + [next_cell], food, visited, path):
                return True

            # Nếu không tìm được đường, quay lui
            visited.remove(next_cell)
            path.pop()

    return False  # Không tìm được đường đi

# Hàm tạo vị trí ngẫu nhiên cho thức ăn
def random_position(snake):
    """
    Tạo vị trí ngẫu nhiên không trùng với thân rắn
    
    Args:
        snake: List các tọa độ phần thân rắn
        
    Returns:
        Tuple (x,y) là vị trí hợp lệ
    """
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos not in snake:
            return pos

# Khởi tạo trạng thái ban đầu của game
snake = [(GRID_SIZE//2, GRID_SIZE//2)]  # Rắn bắt đầu ở giữa màn hình
food = random_position(snake)  # Tạo vị trí thức ăn đầu tiên
score = 0  # Điểm số ban đầu

# Vòng lặp chính của game
running = True
while running:
    # Xử lý các sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Nếu nhấn nút đóng cửa sổ
            running = False
        elif event.type == pygame.KEYDOWN:  # Nếu nhấn phím
            if event.key == pygame.K_ESCAPE:  # Nếu nhấn ESC
                running = False

    # Vẽ màn hình đen
    screen.fill(BLACK)
    
    # Vẽ lưới các ô vuông
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    
    # Vẽ rắn
    for i, segment in enumerate(snake):
        color = GREEN
        if i == len(snake) - 1:  # Nếu là đầu rắn
            # Vẽ đầu rắn
            pygame.draw.rect(screen, color, (segment[0] * CELL_SIZE + 1, segment[1] * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))
            # Vẽ 2 mắt
            pygame.draw.circle(screen, WHITE, 
                (int(segment[0] * CELL_SIZE + CELL_SIZE//4), 
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
            pygame.draw.circle(screen, WHITE,
                (int(segment[0] * CELL_SIZE + 3*CELL_SIZE//4),
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
        else:  # Nếu là thân rắn
            pygame.draw.rect(screen, color, (segment[0] * CELL_SIZE + 1, segment[1] * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))
    
    # Vẽ thức ăn dạng hình tròn
    pygame.draw.circle(screen, RED,
        (int(food[0] * CELL_SIZE + CELL_SIZE//2),
         int(food[1] * CELL_SIZE + CELL_SIZE//2)), CELL_SIZE//3)

    # Tìm đường đi đến thức ăn
    path = []  # Đường đi sẽ tìm được
    visited = set(snake[:-1])  # Đánh dấu thân rắn đã thăm
    if find_path(snake, food, visited, path):  # Nếu tìm được đường
        next_move = path[0]  # Lấy bước đi kế tiếp
        # Vẽ đường đi dự đoán
        for pos in path:
            pygame.draw.rect(screen, BLUE, (pos[0] * CELL_SIZE + CELL_SIZE//3, 
                                          pos[1] * CELL_SIZE + CELL_SIZE//3, 
                                          CELL_SIZE//3, CELL_SIZE//3))
    else:  # Nếu không tìm được đường
        # Tìm các bước đi có thể
        possible_moves = []
        for direction in DIRECTIONS.values():
            temp_move = (snake[-1][0] + direction[0], snake[-1][1] + direction[1])
            if (temp_move not in snake[:-1] and 
                0 <= temp_move[0] < GRID_SIZE and 
                0 <= temp_move[1] < GRID_SIZE):
                possible_moves.append(temp_move)
        
        if possible_moves:  # Nếu có bước đi hợp lệ
            next_move = random.choice(possible_moves)  # Chọn ngẫu nhiên một bước
        else:  # Nếu không có bước đi nào
            print(f"Game Over! Score: {score}")  # In điểm số
            running = False  # Kết thúc game
            continue

    # Cập nhật vị trí rắn
    snake.append(next_move)  # Thêm đầu mới
    if next_move == food:  # Nếu ăn được thức ăn
        food = random_position(snake)  # Tạo thức ăn mới
        score += 1  # Tăng điểm
    else:  # Nếu không ăn được thức ăn
        snake.pop(0)  # Xóa đuôi

    # Kiểm tra va chạm với thân
    head = snake[-1]
    if head in snake[:-1]:  # Nếu đầu đụng thân
        print(f"Game Over! Score: {score}")  # In điểm số
        running = False  # Kết thúc game
        continue

    # Hiển thị điểm số
    font = pygame.font.Font(None, 36)  # Font chữ
    score_text = font.render(f'Score: {score}', True, WHITE)  # Tạo text điểm
    screen.blit(score_text, (10, 10))  # Vẽ text lên màn hình

    # Cập nhật màn hình
    pygame.display.flip()
    clock.tick(5)  # Giới hạn 5 FPS

# Kết thúc pygame và thoát chương trình
pygame.quit()
sys.exit()
