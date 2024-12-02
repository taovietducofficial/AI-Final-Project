"""
Cách thức hoạt động của thuật toán Minimax trong game cờ vua:

1. Khái niệm:
- Là thuật toán tìm kiếm đối kháng cho game 2 người chơi
- Xây dựng cây trò chơi với các nước đi có thể
- Giả định đối thủ luôn chọn nước đi tối ưu
- Tìm nước đi tốt nhất cho người chơi hiện tại

2. Cách hoạt động:
- Xây dựng cây trò chơi:
  + Mỗi nút là một trạng thái bàn cờ
  + Các nhánh là các nước đi có thể
  + Độ sâu tìm kiếm thường là 4-6 tầng
  
- Với mỗi nút trong cây:
  + Nếu là nút lá hoặc đạt độ sâu max:
    * Đánh giá giá trị trạng thái
  + Nếu là tầng MAX (người chơi):
    * Chọn giá trị lớn nhất từ các con
  + Nếu là tầng MIN (đối thủ):
    * Chọn giá trị nhỏ nhất từ các con

- Hàm đánh giá bàn cờ dựa trên:
  + Giá trị quân cờ (tốt=1, mã/tượng=3, xe=5, hậu=9)
  + Vị trí quân cờ trên bàn
  + Khả năng kiểm soát trung tâm
  + Bảo vệ vua
  + Cấu trúc tốt
  + Khả năng tấn công

3. Ưu điểm:
- Tìm được nước đi tối ưu
- Phù hợp với game có luật rõ ràng
- Dễ cài đặt và debug
- Có thể cải tiến bằng Alpha-Beta

4. Nhược điểm:
- Độ phức tạp lớn O(b^d)
  + b: số nước đi trung bình mỗi tầng
  + d: độ sâu tìm kiếm
- Tốn nhiều bộ nhớ
- Chậm với độ sâu lớn
- Cần thiết kế hàm đánh giá tốt

5. Cải tiến có thể:
- Alpha-Beta pruning
- Iterative deepening
- Move ordering
- Transposition table
- Quiescence search
"""


# Import các thư viện cần thiết
import sys  # Thư viện hệ thống để thoát chương trình
import math  # Thư viện toán học để tính toán
import pygame  # Thư viện đồ họa game
import copy  # Thư viện để sao chép đối tượng

# Cấu hình bàn cờ
BOARD_SIZE = 8  # Kích thước bàn cờ 8x8
SQUARE_SIZE = 80  # Kích thước mỗi ô cờ là 80 pixel
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE  # Kích thước cửa sổ game

# Định nghĩa các màu sắc sử dụng trong game
WHITE = (255, 255, 255)  # Màu trắng cho quân cờ trắng
BLACK = (0, 0, 0)  # Màu đen cho quân cờ đen  
LIGHT_GREEN = (144, 238, 144)  # Màu xanh lá nhạt cho ô cờ
DARK_GREEN = (34, 139, 34)  # Màu xanh lá đậm cho ô cờ
HIGHLIGHT = (255, 255, 0)  # Màu vàng để highlight nước đi
SELECTED = (0, 255, 0)  # Màu xanh lá để highlight quân cờ đang chọn
POSSIBLE_MOVE = (0, 200, 255)  # Màu xanh dương để hiển thị nước đi có thể

# Định nghĩa các loại quân cờ
EMPTY = 0  # Ô trống
PAWN = 1  # Tốt
KNIGHT = 2  # Mã
BISHOP = 3  # Tượng  
ROOK = 4  # Xe
QUEEN = 5  # Hậu
KING = 6  # Vua

# Lớp Piece để lưu thông tin quân cờ
class Piece:
    def __init__(self, piece_type, is_white):
        self.piece_type = piece_type  # Loại quân cờ
        self.is_white = is_white  # Màu quân cờ (trắng/đen)

# Hàm khởi tạo bàn cờ ban đầu
def initialize_board():
    # Tạo bàn cờ trống
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Khởi tạo quân cờ trắng
    for i in range(BOARD_SIZE):
        board[6][i] = Piece(PAWN, True)  # Hàng tốt trắng
    # Khởi tạo các quân cờ trắng khác
    board[7][0] = Piece(ROOK, True)
    board[7][1] = Piece(KNIGHT, True) 
    board[7][2] = Piece(BISHOP, True)
    board[7][3] = Piece(QUEEN, True)
    board[7][4] = Piece(KING, True)
    board[7][5] = Piece(BISHOP, True)
    board[7][6] = Piece(KNIGHT, True)
    board[7][7] = Piece(ROOK, True)

    # Khởi tạo quân cờ đen
    for i in range(BOARD_SIZE):
        board[1][i] = Piece(PAWN, False)  # Hàng tốt đen
    # Khởi tạo các quân cờ đen khác
    board[0][0] = Piece(ROOK, False)
    board[0][1] = Piece(KNIGHT, False)
    board[0][2] = Piece(BISHOP, False) 
    board[0][3] = Piece(QUEEN, False)
    board[0][4] = Piece(KING, False)
    board[0][5] = Piece(BISHOP, False)
    board[0][6] = Piece(KNIGHT, False)
    board[0][7] = Piece(ROOK, False)

    return board

# Hàm lấy các nước đi hợp lệ cho một bên
def get_valid_moves(board, is_white):
    moves = []  # Danh sách các nước đi hợp lệ
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None and piece.is_white == is_white:
                # Lấy nước đi cho từng loại quân cờ
                if piece.piece_type == PAWN:
                    moves.extend(get_pawn_moves(board, i, j))
                elif piece.piece_type == KNIGHT:
                    moves.extend(get_knight_moves(board, i, j))
                # Thêm các nước đi cho các quân cờ khác ở đây
    return moves

# Hàm lấy các nước đi hợp lệ cho quân tốt
def get_pawn_moves(board, row, col):
    moves = []  # Danh sách nước đi của tốt
    piece = board[row][col]
    direction = -1 if piece.is_white else 1  # Hướng di chuyển của tốt
    
    # Kiểm tra nước đi thẳng
    if 0 <= row + direction < BOARD_SIZE and board[row + direction][col] is None:
        moves.append(((row, col), (row + direction, col)))
        
    # Kiểm tra nước đi chéo để ăn quân
    for dcol in [-1, 1]:  # Kiểm tra 2 ô chéo
        new_col = col + dcol
        if 0 <= new_col < BOARD_SIZE and 0 <= row + direction < BOARD_SIZE:
            target = board[row + direction][new_col]
            if target is not None and target.is_white != piece.is_white:
                moves.append(((row, col), (row + direction, new_col)))
                
    return moves

# Hàm lấy các nước đi hợp lệ cho quân mã
def get_knight_moves(board, row, col):
    moves = []  # Danh sách nước đi của mã
    piece = board[row][col]
    # Các hướng di chuyển có thể của mã
    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
    
    # Kiểm tra từng hướng di chuyển
    for drow, dcol in knight_moves:
        new_row, new_col = row + drow, col + dcol
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            target = board[new_row][new_col]
            if target is None or target.is_white != piece.is_white:
                moves.append(((row, col), (new_row, new_col)))
                
    return moves

# Hàm thực hiện nước đi
def make_move(board, move):
    from_pos, to_pos = move
    new_board = copy.deepcopy(board)  # Tạo bản sao của bàn cờ
    # Di chuyển quân cờ
    new_board[to_pos[0]][to_pos[1]] = new_board[from_pos[0]][from_pos[1]]
    new_board[from_pos[0]][from_pos[1]] = None
    return new_board

# Hàm vẽ bàn cờ
def draw_board(screen):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Tô màu xen kẽ cho các ô cờ
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                            SQUARE_SIZE, SQUARE_SIZE))

# Hàm vẽ quân cờ
def draw_pieces(screen, board):
    # Định nghĩa ký hiệu Unicode cho các quân cờ
    piece_symbols = {
        PAWN: '♟',
        KNIGHT: '♞',
        BISHOP: '♝',
        ROOK: '♜',
        QUEEN: '♛',
        KING: '♚'
    }
    
    # Cấu hình font chữ
    font = pygame.font.SysFont('segoeuisymbol', 60)
    
    # Vẽ từng quân cờ
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece is not None:
                color = WHITE if piece.is_white else BLACK
                symbol = piece_symbols[piece.piece_type]
                text = font.render(symbol, True, color)
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE//2,
                                                row * SQUARE_SIZE + SQUARE_SIZE//2))
                screen.blit(text, text_rect)

# Hàm đánh giá bàn cờ
def evaluate_board(board):
    score = 0
    # Giá trị của từng loại quân cờ
    piece_values = {
        PAWN: 1,
        KNIGHT: 3,
        BISHOP: 3,
        ROOK: 5,
        QUEEN: 9,
        KING: 0  # Không tính giá trị vua vì game kết thúc khi vua bị chiếu
    }

    # Tính tổng giá trị quân cờ
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None:
                piece_value = piece_values.get(piece.piece_type, 0)
                score += piece_value if piece.is_white else -piece_value
    return score

# Thuật toán Minimax với Alpha-Beta Pruning
def minimax(board, depth, is_maximizing, alpha, beta):
    # Điều kiện dừng
    if depth == 0:
        return evaluate_board(board), None

    # Lấy danh sách nước đi có thể
    possible_moves = get_valid_moves(board, is_maximizing)
    if not possible_moves:
        return evaluate_board(board), None

    best_move = None
    if is_maximizing:  # Lượt của MAX (AI)
        best_score = -math.inf
        for move in possible_moves:
            new_board = make_move(board, move)
            score, _ = minimax(new_board, depth - 1, False, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:  # Cắt tỉa Alpha
                break
        return best_score, best_move
    else:  # Lượt của MIN (người chơi)
        best_score = math.inf
        for move in possible_moves:
            new_board = make_move(board, move)
            score, _ = minimax(new_board, depth - 1, True, alpha, beta)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:  # Cắt tỉa Beta
                break
        return best_score, best_move

# Kiểm tra sự tồn tại của vua
def check_kings(board):
    white_king = False
    black_king = False
    # Duyệt bàn cờ tìm vua
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None and piece.piece_type == KING:
                if piece.is_white:
                    white_king = True
                else:
                    black_king = True
    return white_king, black_king

# Hàm chính
def main():
    # Khởi tạo pygame và cửa sổ game
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Chess Game')
    
    # Khởi tạo trạng thái game
    board = initialize_board()
    running = True
    is_white_turn = True  # AI chơi quân trắng
    game_over = False
    
    # Vòng lặp chính của game
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Vẽ bàn cờ và quân cờ
        screen.fill(WHITE)
        draw_board(screen)
        draw_pieces(screen, board)
        
        # Kiểm tra kết thúc game
        white_king, black_king = check_kings(board)
        if not white_king or not black_king:
            game_over = True
            # Hiển thị thông báo kết thúc
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over!", True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(text, text_rect)
        else:
            if is_white_turn:
                # Lượt của AI (quân trắng)
                score, best_move = minimax(board, 3, True, -math.inf, math.inf)
                if best_move:
                    board = make_move(board, best_move)
                is_white_turn = False
            else:
                # Lượt của người chơi (quân đen)
                # Thêm xử lý nước đi của người chơi ở đây
                pygame.time.wait(1000)  # Thêm độ trễ để quan sát
                is_white_turn = True
        
        # Cập nhật màn hình
        pygame.display.flip()
    
    # Kết thúc game
    pygame.quit()
    sys.exit()

# Chạy game khi chạy trực tiếp file này
if __name__ == "__main__":
    main()
