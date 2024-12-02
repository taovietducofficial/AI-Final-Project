"""
Đây là một chương trình game rắn sử dụng thuật toán A* để tìm đường đi.

Cách thức hoạt động:

1. Khởi tạo:
- Sử dụng pygame để tạo giao diện đồ họa
- Thiết lập màn hình kích thước 600x400 pixels
- Mỗi ô trong lưới có kích thước 20x20 pixels
- Định nghĩa các màu cơ bản: đen, trắng, xanh lá, đỏ

2. Thuật toán A*:
- Sử dụng hàm heuristic() để tính khoảng cách Manhattan giữa 2 điểm
- Hàm astar_search() tìm đường đi ngắn nhất từ điểm đầu đến đích:
  + Duy trì danh sách open_set chứa các điểm cần xét
  + Sử dụng heapq để lấy điểm có chi phí thấp nhất
  + Lưu đường đi trong came_from
  + g_score lưu chi phí thực từ điểm bắt đầu
  + f_score = g_score + heuristic (chi phí ước tính đến đích)
  
3. Game rắn:
- Rắn di chuyển theo đường đi tìm được từ A*
- Tránh va chạm với tường và thân rắn
- Thu thập thức ăn để tăng điểm
- Lưu điểm cao nhất

4. Điều khiển:
- Sử dụng A* để tự động tìm đường đến thức ăn
- Có thể tạm dừng game
- Hiển thị điểm số và điểm cao nhất
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import heapq   # Thư viện để sử dụng hàng đợi ưu tiên trong thuật toán A*
import random  # Thư viện để tạo số ngẫu nhiên

# Khởi tạo pygame để bắt đầu sử dụng các chức năng của thư viện
pygame.init()

# Thiết lập kích thước màn hình và kích thước ô
WIDTH, HEIGHT = 600, 400  # Kích thước màn hình game
CELL_SIZE = 20  # Kích thước mỗi ô vuông trong game

# Định nghĩa các màu sắc sử dụng trong game
BLACK = (0, 0, 0)    # Màu đen cho nền
WHITE = (255, 255, 255)  # Màu trắng cho mắt rắn và text
GREEN = (0, 255, 0)   # Màu xanh lá cho thân rắn
RED = (255, 0, 0)     # Màu đỏ cho thức ăn

# Tạo cửa sổ game và đặt tiêu đề
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with A* Search")

# Biến lưu điểm cao nhất
high_score = 0

# Hàm tính khoảng cách Manhattan giữa 2 điểm
def heuristic(a, b):
    """
    Tính khoảng cách Manhattan giữa 2 điểm a và b
    Khoảng cách Manhattan = |x1-x2| + |y1-y2|
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Thuật toán A* để tìm đường đi
def astar_search(start, goal, obstacles, grid_size):
    """
    Tìm đường đi từ điểm start đến goal, tránh các obstacles
    Sử dụng thuật toán A* với heuristic là khoảng cách Manhattan
    """
    open_set = []  # Danh sách các điểm cần xét
    heapq.heappush(open_set, (0, start))  # Thêm điểm bắt đầu vào open_set
    came_from = {}  # Lưu đường đi
    g_score = {start: 0}  # Chi phí thực từ điểm bắt đầu đến mỗi điểm
    f_score = {start: heuristic(start, goal)}  # Tổng chi phí ước tính

    while open_set:
        _, current = heapq.heappop(open_set)  # Lấy điểm có f_score nhỏ nhất

        if current == goal:  # Nếu đã đến đích
            # Truy vết đường đi
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        # Xét các ô lân cận
        neighbors = [
            (current[0] + 1, current[1]),  # Phải
            (current[0] - 1, current[1]),  # Trái
            (current[0], current[1] + 1),  # Dưới
            (current[0], current[1] - 1),  # Trên
        ]

        # Kiểm tra từng ô lân cận
        for neighbor in neighbors:
            # Kiểm tra ô có hợp lệ không (trong grid và không phải obstacle)
            if (
                0 <= neighbor[0] < grid_size[0]
                and 0 <= neighbor[1] < grid_size[1]
                and neighbor not in obstacles
            ):
                tentative_g_score = g_score[current] + 1  # Chi phí để đi đến ô lân cận

                # Nếu tìm được đường đi tốt hơn đến ô lân cận
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Trả về danh sách rỗng nếu không tìm thấy đường đi

# Thiết lập các thông số ban đầu của game
grid_size = (WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)  # Kích thước lưới game
snake = [(5, 5)]  # Vị trí ban đầu của rắn
snake_dir = (1, 0)  # Hướng di chuyển ban đầu
food = (10, 10)  # Vị trí thức ăn ban đầu
obstacles = set()  # Tập các chướng ngại vật
clock = pygame.time.Clock()  # Đồng hồ để kiểm soát FPS
score = 0  # Điểm số ban đầu

# Thiết lập font chữ để hiển thị điểm
font = pygame.font.Font(None, 36)

# Vòng lặp chính của game
running = True
while running:
    screen.fill(BLACK)  # Xóa màn hình bằng màu đen

    # Vẽ rắn và mắt rắn
    for i, segment in enumerate(snake):
        pygame.draw.rect(
            screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )
        # Vẽ mắt cho đầu rắn
        if i == 0:
            pygame.draw.circle(screen, WHITE, 
                (int(segment[0] * CELL_SIZE + CELL_SIZE//4), 
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
            pygame.draw.circle(screen, WHITE,
                (int(segment[0] * CELL_SIZE + 3*CELL_SIZE//4),
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)

    # Vẽ thức ăn dạng hình tròn
    pygame.draw.circle(screen, RED,
        (int(food[0] * CELL_SIZE + CELL_SIZE//2),
         int(food[1] * CELL_SIZE + CELL_SIZE//2)), CELL_SIZE//2)

    # Hiển thị điểm số và điểm cao nhất
    score_text = font.render(f'Score: {score}', True, WHITE)
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (WIDTH - 200, 10))

    pygame.display.flip()  # Cập nhật màn hình

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    try:
        # Tìm đường đi đến thức ăn bằng A*
        path = astar_search(snake[0], food, set(snake[1:]) | obstacles, grid_size)

        if path:  # Nếu tìm được đường đi
            next_step = path[0]  # Lấy bước đi tiếp theo
            snake.insert(0, next_step)  # Thêm vị trí mới vào đầu rắn

            if next_step == food:  # Nếu ăn được thức ăn
                score += 10  # Tăng điểm
                if score > high_score:
                    high_score = score
                # Tạo thức ăn mới
                attempts = 0
                while attempts < 100:
                    food = (random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1))
                    if food not in snake:
                        break
                    attempts += 1
                if attempts >= 100:  # Nếu không tìm được vị trí mới cho thức ăn
                    print("You Win!")
                    running = False
            else:
                snake.pop()  # Xóa đuôi rắn nếu không ăn được thức ăn
        else:  # Nếu không tìm được đường đi
            print("Game Over!")
            if score > high_score:
                high_score = score
            # Reset game
            snake = [(5, 5)]
            food = (10, 10)
            score = 0
            
    except Exception as e:
        print(f"Error: {e}")
        # Xử lý lỗi bằng cách reset game
        snake = [(5, 5)]
        food = (10, 10)
        score = 0

    clock.tick(10)  # Giới hạn FPS là 10

pygame.quit()  # Đóng pygame khi kết thúc game
