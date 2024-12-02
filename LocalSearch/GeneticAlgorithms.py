"""
Cách thức hoạt động của thuật toán Genetic Algorithm trong game Snake:

1. Khởi tạo quần thể:
- Tạo POPULATION_SIZE cá thể (thường 50-200)
- Mỗi cá thể là một chuỗi gen độ dài GENOME_LENGTH (thường 50-100)
- Mỗi gen là một hướng di chuyển (UP/DOWN/LEFT/RIGHT)
- Gen được tạo ngẫu nhiên ban đầu

2. Đánh giá độ thích nghi (fitness):
- Chạy game với chuỗi di chuyển của mỗi cá thể
- Tính điểm dựa trên:
  + Độ dài rắn đạt được
  + Khoảng cách tới thức ăn
  + Thời gian sống sót
  + Số thức ăn ăn được
  + Độ an toàn của đường đi

3. Chọn lọc tự nhiên:
- Sắp xếp cá thể theo điểm fitness
- Chọn một số cá thể tốt nhất làm bố mẹ
- Phương pháp chọn:
  + Tournament selection
  + Roulette wheel selection
  + Rank selection

4. Lai ghép (crossover):
- Chọn cặp bố mẹ từ nhóm được chọn
- Tạo con bằng cách kết hợp gen:
  + Single-point crossover
  + Two-point crossover
  + Uniform crossover
- Tạo ra số lượng con bằng với quần thể ban đầu

5. Đột biến (mutation):
- Với xác suất MUTATION_RATE (thường 1-5%)
- Thay đổi ngẫu nhiên một số gen
- Giúp đa dạng hóa quần thể
- Tránh bị kẹt ở cực trị địa phương

6. Thế hệ mới:
- Thay thế quần thể cũ bằng con lai
- Giữ lại một số cá thể tốt nhất (elitism)
- Đánh giá lại độ thích nghi
- Lặp lại từ bước 3

7. Điều kiện dừng:
- Đạt số thế hệ tối đa NUM_GENERATIONS
- Hoặc tìm được giải pháp tối ưu
- Hoặc độ thích nghi không cải thiện sau nhiều thế hệ

8. Ưu điểm:
- Khả năng tìm kiếm toàn cục tốt
- Thích nghi với không gian tìm kiếm lớn
- Dễ song song hóa
- Không đòi hỏi thông tin gradient

9. Nhược điểm:
- Hội tụ chậm
- Cần tinh chỉnh nhiều tham số
- Không đảm bảo tìm được tối ưu toàn cục
- Chi phí tính toán cao
"""


# Import các thư viện cần thiết
import pygame  # Thư viện để tạo giao diện game
import random  # Thư viện để tạo số ngẫu nhiên
import numpy as np  # Thư viện để tính toán

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
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']  # Các hướng có thể di chuyển
MOVE_MAP = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}  # Vector di chuyển tương ứng

# Các tham số cho thuật toán di truyền
POPULATION_SIZE = 100  # Số lượng cá thể trong quần thể
GENOME_LENGTH = 50    # Độ dài chuỗi gen của mỗi cá thể
MUTATION_RATE = 0.2   # Tỷ lệ đột biến gen
NUM_GENERATIONS = 200 # Số thế hệ tối đa

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
        move_x, move_y = MOVE_MAP[action]  # Lấy vector di chuyển
        new_head = (head_x + move_x * CELL_SIZE, head_y + move_y * CELL_SIZE)  # Tính vị trí đầu mới
        
        new_snake = [new_head] + self.snake[:-1]  # Tạo thân rắn mới
        if new_head == self.food:  # Nếu ăn được thức ăn
            new_snake.append(self.snake[-1])  # Thêm một đốt vào đuôi
            # Tạo thức ăn mới ngẫu nhiên
            self.food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                        random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)
        return GameState(new_snake, self.food, action)

    # Kiểm tra trạng thái có hợp lệ không
    def is_valid(self, width, height):
        head = self.snake[0]
        # Kiểm tra rắn trong màn hình và không đâm vào thân
        return (0 <= head[0] < width and 0 <= head[1] < height and
                len(self.snake) == len(set(self.snake)))

    # Hàm đánh giá độ thích nghi
    def fitness(self):
        head = self.snake[0]
        # Tính khoảng cách Manhattan đến thức ăn
        distance = -abs(head[0] - self.food[0]) - abs(head[1] - self.food[1])
        score_bonus = self.score * 1000  # Thưởng điểm cho việc ăn được mồi
        return distance + score_bonus

# Các hàm của thuật toán di truyền
def create_population():
    # Tạo quần thể ban đầu với các chuỗi gen ngẫu nhiên
    return [random.choices(DIRECTIONS, k=GENOME_LENGTH) for _ in range(POPULATION_SIZE)]

def evaluate_population(population, game_state, width, height):
    # Đánh giá độ thích nghi của từng cá thể trong quần thể
    scores = []
    for genome in population:
        state = game_state
        steps = 0
        for action in genome:
            if not state.is_valid(width, height):
                break
            next_state = state.next_state(action)
            if next_state.score > state.score:  # Nếu ăn được mồi
                steps = 0  # Reset số bước
            else:
                steps += 1
            if steps > 50:  # Nếu đi quá nhiều bước không ăn được mồi
                break
            state = next_state
        scores.append(state.fitness())
    return scores

def select_population(population, scores):
    # Chọn lọc cá thể bằng phương pháp tournament
    selected = []
    for _ in range(POPULATION_SIZE // 2):
        tournament = random.sample(list(zip(scores, population)), 5)
        winner = max(tournament, key=lambda x: x[0])[1]
        selected.append(winner)
    return selected

def crossover(parent1, parent2):
    # Lai ghép hai điểm
    point1, point2 = sorted(random.sample(range(GENOME_LENGTH), 2))
    child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    return child

def mutate(genome):
    # Đột biến gen với xác suất MUTATION_RATE
    mutated = genome.copy()
    for i in range(len(mutated)):
        if random.random() < MUTATION_RATE:
            mutated[i] = random.choice(DIRECTIONS)
    return mutated

def next_generation(selected_population):
    # Tạo thế hệ mới từ quần thể đã chọn
    new_population = []
    while len(new_population) < POPULATION_SIZE:
        parent1, parent2 = random.sample(selected_population, 2)
        child1 = mutate(crossover(parent1, parent2))
        child2 = mutate(crossover(parent2, parent1))
        new_population.extend([child1, child2])
    return new_population[:POPULATION_SIZE]

# Hàm chính của game
def main():
    # Khởi tạo màn hình và các thông số cơ bản
    screen = pygame.display.set_mode((WIDTH, HEIGHT + SCORE_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Game - Genetic Algorithm")

    # Khởi tạo font chữ
    font = pygame.font.Font(None, 36)

    # Khởi tạo rắn và thức ăn
    snake = [(WIDTH // 2, HEIGHT // 2)]
    food = (random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE)

    game_state = GameState(snake, food, 'UP')
    running = True
    best_score = 0

    # Bắt đầu thuật toán di truyền
    population = create_population()

    # Vòng lặp chính của game
    for generation in range(NUM_GENERATIONS):
        # Đánh giá và phát triển quần thể
        scores = evaluate_population(population, game_state, WIDTH, HEIGHT)
        selected_population = select_population(population, scores)
        population = next_generation(selected_population)

        # Sử dụng genome tốt nhất để di chuyển
        best_genome = selected_population[0]
        for action in best_genome:
            game_state = game_state.next_state(action)
            if not game_state.is_valid(WIDTH, HEIGHT):
                running = False
                break

            # Vẽ game
            # Vẽ khu vực điểm số
            screen.fill(SCORE_BG)
            # Vẽ khu vực chơi game
            pygame.draw.rect(screen, BLACK, (0, SCORE_HEIGHT, WIDTH, HEIGHT))

            # Vẽ rắn với hiệu ứng nâng cao
            for i, segment in enumerate(game_state.snake):
                adjusted_y = segment[1] + SCORE_HEIGHT
                if i == 0:  # Vẽ đầu rắn
                    pygame.draw.rect(screen, SNAKE_HEAD, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 2)
                    # Vẽ mắt cho rắn
                    eye_radius = 3
                    pygame.draw.circle(screen, WHITE, (segment[0] + CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                    pygame.draw.circle(screen, WHITE, (segment[0] + 3*CELL_SIZE//4, adjusted_y + CELL_SIZE//3), eye_radius)
                else:  # Vẽ thân rắn
                    pygame.draw.rect(screen, SNAKE_BODY, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, SNAKE_BORDER, (segment[0], adjusted_y, CELL_SIZE, CELL_SIZE), 1)

            # Vẽ thức ăn
            food_y = game_state.food[1] + SCORE_HEIGHT
            pygame.draw.circle(screen, RED, (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2)
            pygame.draw.circle(screen, (200, 0, 0), (game_state.food[0] + CELL_SIZE//2, food_y + CELL_SIZE//2), CELL_SIZE//2 - 2)
            
            # Hiển thị điểm số và thông tin
            score_text = font.render(f'Score: {game_state.score}', True, WHITE)
            high_score_text = font.render(f'High Score: {best_score}', True, WHITE)
            gen_text = font.render(f'Generation: {generation}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))
            screen.blit(gen_text, (10, 40))
            
            pygame.display.flip()
            clock.tick(20)  # Điều chỉnh tốc độ game

            # Cập nhật điểm cao nhất
            if game_state.score > best_score:
                best_score = game_state.score
                print(f"New high score {best_score} at generation {generation}")

        if not running:
            break

    print(f"Game Over! Final Score: {game_state.score}")
    
    # Chờ người dùng đóng cửa sổ
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    
    pygame.quit()

# Chạy game khi file được thực thi trực tiếp
if __name__ == "__main__":
    main()
