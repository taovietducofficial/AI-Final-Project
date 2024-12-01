import pygame
import heapq
import random

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Thiết lập màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with A* Search")

# High score
high_score = 0

# Hàm heuristic (Manhattan Distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Hàm tìm đường sử dụng A* Search
def astar_search(start, goal, obstacles, grid_size):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        neighbors = [
            (current[0] + 1, current[1]),
            (current[0] - 1, current[1]),
            (current[0], current[1] + 1),
            (current[0], current[1] - 1),
        ]

        for neighbor in neighbors:
            if (
                0 <= neighbor[0] < grid_size[0]
                and 0 <= neighbor[1] < grid_size[1]
                and neighbor not in obstacles
            ):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Trả về danh sách rỗng nếu không tìm thấy đường đi

# Cấu hình game
grid_size = (WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)
snake = [(5, 5)]
snake_dir = (1, 0)
food = (10, 10)
obstacles = set()
clock = pygame.time.Clock()
score = 0

# Font cho điểm số
font = pygame.font.Font(None, 36)

running = True
while running:
    screen.fill(BLACK)

    # Vẽ rắn và thức ăn
    for i, segment in enumerate(snake):
        pygame.draw.rect(
            screen, GREEN, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )
        # Vẽ mắt cho đầu rắn
        if i == 0:
            # Mắt trái
            pygame.draw.circle(screen, WHITE, 
                (int(segment[0] * CELL_SIZE + CELL_SIZE//4), 
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
            # Mắt phải
            pygame.draw.circle(screen, WHITE,
                (int(segment[0] * CELL_SIZE + 3*CELL_SIZE//4),
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)

    # Vẽ thức ăn (hình tròn thay vì hình vuông)
    pygame.draw.circle(screen, RED,
        (int(food[0] * CELL_SIZE + CELL_SIZE//2),
         int(food[1] * CELL_SIZE + CELL_SIZE//2)), CELL_SIZE//2)

    # Hiển thị điểm số và điểm cao nhất
    score_text = font.render(f'Score: {score}', True, WHITE)
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (WIDTH - 200, 10))

    pygame.display.flip()

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    try:
        # Tìm đường đến thức ăn bằng A*
        path = astar_search(snake[0], food, set(snake[1:]) | obstacles, grid_size)

        if path:
            next_step = path[0]
            snake.insert(0, next_step)

            if next_step == food:
                # Tăng điểm
                score += 10
                if score > high_score:
                    high_score = score
                # Sinh thức ăn mới
                attempts = 0
                while attempts < 100:  # Giới hạn số lần thử
                    food = (random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1))
                    if food not in snake:
                        break
                    attempts += 1
                if attempts >= 100:  # Nếu không tìm được vị trí mới sau 100 lần thử
                    print("You Win!")
                    running = False
            else:
                # Di chuyển rắn
                snake.pop()
        else:
            print("Game Over!")
            if score > high_score:
                high_score = score
            # Reset game thay vì thoát
            snake = [(5, 5)]
            food = (10, 10)
            score = 0
            
    except Exception as e:
        print(f"Error: {e}")
        # Xử lý lỗi bằng cách reset game
        snake = [(5, 5)]
        food = (10, 10)
        score = 0

    clock.tick(10)

pygame.quit()
