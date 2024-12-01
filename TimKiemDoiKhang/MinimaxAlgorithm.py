import sys
import math
import pygame
import copy

BOARD_SIZE = 8
SQUARE_SIZE = 80  # Kích thước mỗi ô cờ
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE

# Màu sắc
WHITE = (255, 255, 255)  # Màu trắng cho quân cờ trắng
BLACK = (0, 0, 0)  # Màu đen cho quân cờ đen
LIGHT_GREEN = (144, 238, 144)  # Màu xanh lá nhạt cho ô cờ
DARK_GREEN = (34, 139, 34)  # Màu xanh lá đậm cho ô cờ
HIGHLIGHT = (255, 255, 0)  # Màu vàng để highlight nước đi
SELECTED = (0, 255, 0)  # Màu xanh lá để highlight quân cờ đang chọn
POSSIBLE_MOVE = (0, 200, 255)  # Màu xanh dương để hiển thị nước đi có thể

# Các quân cờ
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

# Cấu trúc để lưu thông tin quân cờ
class Piece:
    def __init__(self, piece_type, is_white):
        self.piece_type = piece_type
        self.is_white = is_white

# Khởi tạo bảng cờ
def initialize_board():
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Khởi tạo quân cờ trắng
    for i in range(BOARD_SIZE):
        board[6][i] = Piece(PAWN, True)
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
        board[1][i] = Piece(PAWN, False)
    board[0][0] = Piece(ROOK, False)
    board[0][1] = Piece(KNIGHT, False)
    board[0][2] = Piece(BISHOP, False)
    board[0][3] = Piece(QUEEN, False)
    board[0][4] = Piece(KING, False)
    board[0][5] = Piece(BISHOP, False)
    board[0][6] = Piece(KNIGHT, False)
    board[0][7] = Piece(ROOK, False)

    return board

def get_valid_moves(board, is_white):
    moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None and piece.is_white == is_white:
                if piece.piece_type == PAWN:
                    moves.extend(get_pawn_moves(board, i, j))
                elif piece.piece_type == KNIGHT:
                    moves.extend(get_knight_moves(board, i, j))
                # Add other piece moves here
    return moves

def get_pawn_moves(board, row, col):
    moves = []
    piece = board[row][col]
    direction = -1 if piece.is_white else 1
    
    # Forward move
    if 0 <= row + direction < BOARD_SIZE and board[row + direction][col] is None:
        moves.append(((row, col), (row + direction, col)))
        
    # Capture moves
    for dcol in [-1, 1]:
        new_col = col + dcol
        if 0 <= new_col < BOARD_SIZE and 0 <= row + direction < BOARD_SIZE:
            target = board[row + direction][new_col]
            if target is not None and target.is_white != piece.is_white:
                moves.append(((row, col), (row + direction, new_col)))
                
    return moves

def get_knight_moves(board, row, col):
    moves = []
    piece = board[row][col]
    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
    
    for drow, dcol in knight_moves:
        new_row, new_col = row + drow, col + dcol
        if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
            target = board[new_row][new_col]
            if target is None or target.is_white != piece.is_white:
                moves.append(((row, col), (new_row, new_col)))
                
    return moves

def make_move(board, move):
    from_pos, to_pos = move
    new_board = copy.deepcopy(board)
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

# Hàm vẽ quân cờ
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

# Hàm đánh giá bàn cờ (giá trị của các quân cờ)
def evaluate_board(board):
    score = 0
    piece_values = {
        PAWN: 1,
        KNIGHT: 3,
        BISHOP: 3,
        ROOK: 5,
        QUEEN: 9,
        KING: 0  # Giá trị của quân Vua không tính vì game kết thúc khi vua bị chiếu
    }

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            piece = board[i][j]
            if piece is not None:
                piece_value = piece_values.get(piece.piece_type, 0)
                score += piece_value if piece.is_white else -piece_value
    return score

# Thuật toán Minimax với Alpha-Beta Pruning
def minimax(board, depth, is_maximizing, alpha, beta):
    if depth == 0:
        return evaluate_board(board), None

    possible_moves = get_valid_moves(board, is_maximizing)
    if not possible_moves:
        return evaluate_board(board), None

    best_move = None
    if is_maximizing:
        best_score = -math.inf
        for move in possible_moves:
            new_board = make_move(board, move)
            score, _ = minimax(new_board, depth - 1, False, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = math.inf
        for move in possible_moves:
            new_board = make_move(board, move)
            score, _ = minimax(new_board, depth - 1, True, alpha, beta)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move

# Kiểm tra xem có vua trên bàn cờ không
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
    pygame.display.set_caption('Chess Game')
    
    board = initialize_board()
    running = True
    is_white_turn = True
    game_over = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill(WHITE)
        draw_board(screen)
        draw_pieces(screen, board)
        
        # Kiểm tra vua
        white_king, black_king = check_kings(board)
        if not white_king or not black_king:
            game_over = True
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over!", True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(text, text_rect)
        else:
            if is_white_turn:
                # AI's turn (white)
                score, best_move = minimax(board, 3, True, -math.inf, math.inf)
                if best_move:
                    board = make_move(board, best_move)
                is_white_turn = False
            else:
                # Wait for player's move (black)
                # Add player move handling here
                pygame.time.wait(1000)  # Add delay for visualization
                is_white_turn = True
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
