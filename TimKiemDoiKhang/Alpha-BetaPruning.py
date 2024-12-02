"""
Cách thức hoạt động của thuật toán Alpha-Beta Pruning trong game cờ vua:

1. Khái niệm:
- Là phiên bản cải tiến của thuật toán Minimax
- Cắt tỉa các nhánh không cần thiết để giảm không gian tìm kiếm
- Sử dụng 2 giá trị alpha và beta để đánh dấu giới hạn
  + Alpha: giá trị tốt nhất cho MAX (người chơi)
  + Beta: giá trị tốt nhất cho MIN (đối thủ)

2. Cách hoạt động:
- Khởi tạo:
  + alpha = -∞ 
  + beta = +∞
  + depth = độ sâu tìm kiếm (thường 4-6)

- Với mỗi nút trong cây tìm kiếm:
  + Nếu là nút MAX (người chơi):
    * Duyệt các nước đi có thể
    * Cập nhật alpha = max(alpha, giá_trị_con)
    * Cắt tỉa nếu alpha >= beta
  + Nếu là nút MIN (đối thủ):
    * Duyệt các nước đi có thể  
    * Cập nhật beta = min(beta, giá_trị_con)
    * Cắt tỉa nếu alpha >= beta

- Hàm đánh giá bàn cờ dựa trên:
  + Giá trị quân cờ
  + Vị trí quân cờ trên bàn
  + Khả năng kiểm soát trung tâm
  + Bảo vệ vua
  + Cấu trúc tốt
  + Khả năng tấn công

3. Ưu điểm:
- Giảm đáng kể số nút cần duyệt
- Tìm được nước đi tối ưu như Minimax
- Thời gian chạy nhanh hơn nhiều
- Có thể tìm kiếm sâu hơn

4. Nhược điểm:
- Vẫn có độ phức tạp lớn với độ sâu cao
- Cần thiết kế hàm đánh giá tốt
- Khó cài đặt và debug
- Hiệu quả phụ thuộc thứ tự duyệt nước đi

5. Cải tiến có thể:
- Sắp xếp nước đi theo độ ưu tiên
- Lưu trữ bảng băm các trạng thái
- Tìm kiếm theo chiều sâu lặp
- Cắt tỉa null-move
- Song song hóa tính toán
"""


# Import các thư viện cần thiết
import sys  # Thư viện hệ thống
import math  # Thư viện toán học
import pygame  # Thư viện đồ họa game
import copy  # Thư viện để sao chép đối tượng
from concurrent.futures import ThreadPoolExecutor  # Thư viện để chạy đa luồng

# Các hằng số cho bàn cờ
BOARD_SIZE = 8  # Kích thước bàn cờ 8x8
SQUARE_SIZE = 80  # Kích thước mỗi ô cờ (pixel)
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

# Lớp đối tượng quân cờ
class Piece:
    def __init__(self, piece_type, is_white):
        self.piece_type = piece_type  # Loại quân cờ
        self.is_white = is_white  # Màu quân cờ (trắng/đen)

# Hàm khởi tạo bàn cờ với vị trí ban đầu của các quân cờ
def initialize_board():
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # Tạo bàn cờ trống

    # Đặt các quân cờ trắng
    for i in range(BOARD_SIZE):
        board[6][i] = Piece(PAWN, True)  # Hàng tốt trắng
    # Đặt các quân cờ trắng khác
    board[7][0] = Piece(ROOK, True)
    board[7][1] = Piece(KNIGHT, True)
    board[7][2] = Piece(BISHOP, True)
    board[7][3] = Piece(QUEEN, True)
    board[7][4] = Piece(KING, True)
    board[7][5] = Piece(BISHOP, True)
    board[7][6] = Piece(KNIGHT, True)
    board[7][7] = Piece(ROOK, True)

    # Đặt các quân cờ đen
    for i in range(BOARD_SIZE):
        board[1][i] = Piece(PAWN, False)  # Hàng tốt đen
    # Đặt các quân cờ đen khác
    board[0][0] = Piece(ROOK, False)
    board[0][1] = Piece(KNIGHT, False)
    board[0][2] = Piece(BISHOP, False)
    board[0][3] = Piece(QUEEN, False)
    board[0][4] = Piece(KING, False)
    board[0][5] = Piece(BISHOP, False)
    board[0][6] = Piece(KNIGHT, False)
    board[0][7] = Piece(ROOK, False)

    return board

# Hàm lấy tất cả các nước đi hợp lệ cho một bên
def get_valid_moves(board, is_white):
    moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None and piece.is_white == is_white:
                # Lấy các nước đi hợp lệ cho từng loại quân cờ
                if piece.piece_type == PAWN:
                    moves.extend(get_pawn_moves(board, i, j))
                elif piece.piece_type == KNIGHT:
                    moves.extend(get_knight_moves(board, i, j))
                elif piece.piece_type == BISHOP:
                    moves.extend(get_bishop_moves(board, i, j))
                elif piece.piece_type == ROOK:
                    moves.extend(get_rook_moves(board, i, j))
                elif piece.piece_type == QUEEN:
                    moves.extend(get_queen_moves(board, i, j))
                elif piece.piece_type == KING:
                    moves.extend(get_king_moves(board, i, j))
    return moves

# Hàm lấy các nước đi hợp lệ cho quân tốt
def get_pawn_moves(board, row, col):
    moves = []
    piece = board[row][col]
    direction = -1 if piece.is_white else 1  # Hướng di chuyển (lên/xuống)
    
    # Di chuyển thẳng
    if 0 <= row + direction < BOARD_SIZE and board[row + direction][col] is None:
        moves.append(((row, col), (row + direction, col)))
        # Di chuyển 2 ô từ vị trí ban đầu
        if (piece.is_white and row == 6) or (not piece.is_white and row == 1):
            if board[row + 2*direction][col] is None:
                moves.append(((row, col), (row + 2*direction, col)))
        
    # Ăn chéo
    for dcol in [-1, 1]:
        new_col = col + dcol
        if 0 <= new_col < BOARD_SIZE and 0 <= row + direction < BOARD_SIZE:
            target = board[row + direction][new_col]
            if target is not None and target.is_white != piece.is_white:
                moves.append(((row, col), (row + direction, new_col)))
                
    return moves

# Hàm lấy các nước đi hợp lệ cho quân mã
def get_knight_moves(board, row, col):
    moves = []
    piece = board[row][col]
    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]  # Các hướng di chuyển của mã
    
    for drow, dcol in knight_moves:
        new_row, new_col = row + drow, col + dcol
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            target = board[new_row][new_col]
            if target is None or target.is_white != piece.is_white:
                moves.append(((row, col), (new_row, new_col)))
                
    return moves

# Hàm lấy các nước đi hợp lệ cho quân tượng
def get_bishop_moves(board, row, col):
    moves = []
    piece = board[row][col]
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Các hướng đường chéo
    
    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        while 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            target = board[new_row][new_col]
            if target is None:
                moves.append(((row, col), (new_row, new_col)))
            elif target.is_white != piece.is_white:
                moves.append(((row, col), (new_row, new_col)))
                break
            else:
                break
            new_row += drow
            new_col += dcol
    return moves

# Hàm lấy các nước đi hợp lệ cho quân xe
def get_rook_moves(board, row, col):
    moves = []
    piece = board[row][col]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Các hướng ngang dọc
    
    for drow, dcol in directions:
        new_row, new_col = row + drow, col + dcol
        while 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            target = board[new_row][new_col]
            if target is None:
                moves.append(((row, col), (new_row, new_col)))
            elif target.is_white != piece.is_white:
                moves.append(((row, col), (new_row, new_col)))
                break
            else:
                break
            new_row += drow
            new_col += dcol
    return moves

# Hàm lấy các nước đi hợp lệ cho quân hậu (kết hợp tượng và xe)
def get_queen_moves(board, row, col):
    return get_bishop_moves(board, row, col) + get_rook_moves(board, row, col)

# Hàm lấy các nước đi hợp lệ cho quân vua
def get_king_moves(board, row, col):
    moves = []
    piece = board[row][col]
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                 (0, 1), (1, -1), (1, 0), (1, 1)]  # Tất cả các hướng
    
    for drow, dcol in directions:
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
    new_board[to_pos[0]][to_pos[1]] = new_board[from_pos[0]][from_pos[1]]
    new_board[from_pos[0]][from_pos[1]] = None
    return new_board

# Hàm vẽ bàn cờ
def draw_board(screen):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                            SQUARE_SIZE, SQUARE_SIZE))

# Hàm vẽ các quân cờ
def draw_pieces(screen, board):
    piece_symbols = {
        PAWN: '♟',
        KNIGHT: '♞',
        BISHOP: '♝',
        ROOK: '♜',
        QUEEN: '♛',
        KING: '♚'
    }
    
    font = pygame.font.SysFont('segoeuisymbol', 60)
    
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
        PAWN: 100,
        KNIGHT: 320,
        BISHOP: 330,
        ROOK: 500,
        QUEEN: 900,
        KING: 20000
    }
    
    # Bảng điểm vị trí cho các quân cờ
    position_scores = {
        PAWN: [  # Điểm cho vị trí của quân tốt
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ],
        KNIGHT: [  # Điểm cho vị trí của quân mã
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
    }

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None:
                value = piece_values[piece.piece_type]
                
                # Cộng điểm cho vị trí tốt
                if piece.piece_type in position_scores:
                    pos_score = position_scores[piece.piece_type][i][j]
                    value += pos_score if piece.is_white else -pos_score
                
                score += value if piece.is_white else -value
                
                # Trừ điểm cho quân tốt bị cô lập
                if piece.piece_type == PAWN:
                    isolated = True
                    for di in [-1, 1]:
                        if 0 <= j + di < BOARD_SIZE:
                            if board[i][j+di] is not None and board[i][j+di].piece_type == PAWN:
                                isolated = False
                                break
                    if isolated:
                        score -= 10 if piece.is_white else 10
    
    return score

# Thuật toán Alpha-Beta Pruning
def alpha_beta(board, depth, alpha, beta, is_maximizing):
    if depth == 0:  # Đạt đến độ sâu tối đa
        return evaluate_board(board), None
    
    possible_moves = get_valid_moves(board, is_maximizing)
    if not possible_moves:  # Không còn nước đi
        return evaluate_board(board), None
    
    best_move = None
    if is_maximizing:  # Lượt của người chơi tối đa (trắng)
        max_eval = float('-inf')
        for move in possible_moves:
            new_board = make_move(board, move)
            eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa beta
        return max_eval, best_move
    else:  # Lượt của người chơi tối thiểu (đen)
        min_eval = float('inf')
        for move in possible_moves:
            new_board = make_move(board, move)
            eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa alpha
        return min_eval, best_move

# Kiểm tra sự tồn tại của vua
def check_kings(board):
    white_king = False
    black_king = False
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
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption('Chess Game with Alpha-Beta Pruning')
    clock = pygame.time.Clock()
    
    board = initialize_board()  # Khởi tạo bàn cờ
    running = True
    is_white_turn = True  # Lượt chơi của trắng
    game_over = False
    winner = None
    
    # Tạo ThreadPoolExecutor cho AI
    executor = ThreadPoolExecutor(max_workers=2)
    ai_future = None
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill(WHITE)
        draw_board(screen)
        draw_pieces(screen, board)
        
        # Kiểm tra vua còn sống
        white_king, black_king = check_kings(board)
        if not white_king:
            game_over = True
            winner = "Black"
        elif not black_king:
            game_over = True
            winner = "White"
            
        if game_over:
            # Hiển thị người chiến thắng
            font = pygame.font.Font(None, 74)
            text = font.render(f"{winner} wins!", True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(text, text_rect)
        else:
            if ai_future is None:
                # Bắt đầu tính toán AI trong thread riêng
                ai_future = executor.submit(alpha_beta, board, 3, float('-inf'), float('inf'), is_white_turn)
            elif ai_future.done():
                # Lấy kết quả từ AI và thực hiện nước đi
                score, best_move = ai_future.result()
                if best_move:
                    board = make_move(board, best_move)
                is_white_turn = not is_white_turn
                ai_future = None
        
        pygame.display.flip()
        clock.tick(60)  # Giới hạn FPS
    
    executor.shutdown()
    pygame.quit()
    sys.exit()

# Chạy chương trình
if __name__ == "__main__":
    main()
