import pygame
import sys
import random

# Khởi tạo Pygame
pygame.init()

# Kích thước ô và màn hình
CELL_SIZE = 40  # Tăng kích thước ô để dễ nhìn hơn
GRID_SIZE = 15  # Giảm kích thước lưới để dễ chơi hơn 
SCREEN_SIZE = CELL_SIZE * GRID_SIZE
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Snake Game with Backtracking")
clock = pygame.time.Clock()

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Màu cho đường đi dự đoán

# Hướng di chuyển
DIRECTIONS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}

# Hàm tìm đường với Backtracking
def find_path(snake, food, visited, path):
    head = snake[-1]
    if head == food:
        return True

    # Sắp xếp các hướng theo khoảng cách đến thức ăn
    directions = list(DIRECTIONS.values())
    directions.sort(key=lambda d: abs(head[0] + d[0] - food[0]) + abs(head[1] + d[1] - food[1]))

    for direction in directions:
        next_cell = (head[0] + direction[0], head[1] + direction[1])

        # Kiểm tra ô hợp lệ
        if (
            0 <= next_cell[0] < GRID_SIZE
            and 0 <= next_cell[1] < GRID_SIZE
            and next_cell not in visited
            and next_cell not in snake[:-1]
        ):
            visited.add(next_cell)
            path.append(next_cell)

            if find_path(snake + [next_cell], food, visited, path):
                return True

            visited.remove(next_cell)
            path.pop()

    return False

# Hàm sinh tọa độ ngẫu nhiên
def random_position(snake):
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos not in snake:
            return pos

# Khởi tạo trò chơi
snake = [(GRID_SIZE//2, GRID_SIZE//2)]  # Bắt đầu ở giữa màn hình
food = random_position(snake)
score = 0

# Vòng lặp chính
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Vẽ màn hình
    screen.fill(BLACK)
    
    # Vẽ lưới
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    
    # Vẽ rắn
    for i, segment in enumerate(snake):
        color = GREEN
        if i == len(snake) - 1:  # Đầu rắn
            pygame.draw.rect(screen, color, (segment[0] * CELL_SIZE + 1, segment[1] * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))
            # Vẽ mắt
            pygame.draw.circle(screen, WHITE, 
                (int(segment[0] * CELL_SIZE + CELL_SIZE//4), 
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
            pygame.draw.circle(screen, WHITE,
                (int(segment[0] * CELL_SIZE + 3*CELL_SIZE//4),
                 int(segment[1] * CELL_SIZE + CELL_SIZE//4)), 3)
        else:  # Thân rắn
            pygame.draw.rect(screen, color, (segment[0] * CELL_SIZE + 1, segment[1] * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))
    
    # Vẽ thức ăn (hình tròn)
    pygame.draw.circle(screen, RED,
        (int(food[0] * CELL_SIZE + CELL_SIZE//2),
         int(food[1] * CELL_SIZE + CELL_SIZE//2)), CELL_SIZE//3)

    # Tìm đường
    path = []
    visited = set(snake[:-1])
    if find_path(snake, food, visited, path):
        next_move = path[0]
        # Vẽ đường đi dự đoán
        for pos in path:
            pygame.draw.rect(screen, BLUE, (pos[0] * CELL_SIZE + CELL_SIZE//3, 
                                          pos[1] * CELL_SIZE + CELL_SIZE//3, 
                                          CELL_SIZE//3, CELL_SIZE//3))
    else:
        # Nếu không tìm được đường, đi ngẫu nhiên
        possible_moves = []
        for direction in DIRECTIONS.values():
            temp_move = (snake[-1][0] + direction[0], snake[-1][1] + direction[1])
            if (temp_move not in snake[:-1] and 
                0 <= temp_move[0] < GRID_SIZE and 
                0 <= temp_move[1] < GRID_SIZE):
                possible_moves.append(temp_move)
        
        if possible_moves:
            next_move = random.choice(possible_moves)
        else:
            print(f"Game Over! Score: {score}")
            running = False
            continue

    # Cập nhật vị trí rắn
    snake.append(next_move)
    if next_move == food:
        food = random_position(snake)
        score += 1
    else:
        snake.pop(0)

    # Kiểm tra va chạm
    head = snake[-1]
    if head in snake[:-1]:  # Kiểm tra đầu rắn có đụng vào thân hay không
        print(f"Game Over! Score: {score}")
        running = False
        continue

    # Hiển thị điểm số
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(5)  # Giảm tốc độ game để dễ theo dõi

pygame.quit()
sys.exit()
