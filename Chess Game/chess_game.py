import pygame
import requests
import io
import logging

pygame.init()

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='chess_game.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

BOARD_WIDTH, HEIGHT = 800, 800
INSTRUCTIONS_WIDTH = 450  # Extra space for the instructions
WINDOW_WIDTH = BOARD_WIDTH + INSTRUCTIONS_WIDTH
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
pygame.display.set_caption('Chess Game')

ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_WIDTH // COLS

WHITE = (235, 235, 208)
BLACK = (119, 148, 85)
BACKGROUND_COLOR = (200, 200, 200)
BUTTON_COLOR = (100, 100, 100)
HIGHLIGHT_COLOR = (170, 170, 170)

# Global variables
current_player = 'w'
game_over = False
move_history = []

# Button coordinates for "Best Move" and "Resign"
BEST_MOVE_BUTTON = pygame.Rect(BOARD_WIDTH + 20, HEIGHT - 100, 120, 40)
RESIGN_BUTTON = pygame.Rect(BOARD_WIDTH + 160, HEIGHT - 100, 120, 40)

# Piece image URLs
piece_image_urls = {
    'w_pawn':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wp.png',
    'w_rook':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wr.png',
    'w_knight': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wn.png',
    'w_bishop': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wb.png',
    'w_queen':  'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wq.png',
    'w_king':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wk.png',
    'b_pawn':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bp.png',
    'b_rook':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/br.png',
    'b_knight': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bn.png',
    'b_bishop': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bb.png',
    'b_queen':  'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bq.png',
    'b_king':   'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bk.png',
}

def load_images():
    pieces = {}
    for piece_name, url in piece_image_urls.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            image_data = response.content
            image_file = io.BytesIO(image_data)
            image = pygame.image.load(image_file).convert_alpha()
            image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            pieces[piece_name] = image
        except Exception as e:
            logging.error(f"Error loading {piece_name}: {e}")
            print(f"Error loading {piece_name}: {e}")
    return pieces

def draw_board(window):
    colors = [WHITE, BLACK]
    font = pygame.font.SysFont('Arial', 24, bold=True)
    letters = 'abcdefgh'
    numbers = '12345678'

    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE
            pygame.draw.rect(window, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            # Draw rank numbers (1-8) along the left and right edges
            if col == 0:
                # Left side numbers
                number = font.render(numbers[7 - row], True, (0, 0, 0))
                window.blit(number, (x + 5, y + 5))

            # Draw file letters (a-h) along the top and bottom edges
            if row == ROWS - 1:
                # Bottom letters
                letter = font.render(letters[col], True, (0, 0, 0))
                window.blit(letter, (x + SQUARE_SIZE - 20, y + SQUARE_SIZE - 25))


def draw_pieces(window, board, exclude_piece=None):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.board[row][col]
            if piece is not None and piece != exclude_piece:
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                window.blit(piece.image, (x, y))

def highlight_valid_moves(window, moves):
    for move in moves:
        row, col = move
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)  # Transparency
        s.fill((255, 0 , 0))  # Green highlight
        window.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_button(window, rect, text, font, active=False):
    color = HIGHLIGHT_COLOR if active else BUTTON_COLOR
    pygame.draw.rect(window, color, rect)
    button_text = font.render(text, True, (255, 255, 255))
    window.blit(button_text, (
        rect.x + (rect.width - button_text.get_width()) // 2,
        rect.y + (rect.height - button_text.get_height()) // 2
    ))

def draw_instructions(window, font, current_player, best_move_text):
    # Sidebar background
    pygame.draw.rect(window, BACKGROUND_COLOR, (BOARD_WIDTH, 0, INSTRUCTIONS_WIDTH, HEIGHT))
    
    # Title
    title = font.render("Chess Instructions", True, (0, 0, 0))
    window.blit(title, (BOARD_WIDTH + 20, 20))

    # Current player info
    player_color = (255, 255, 255) if current_player == 'w' else (0, 0, 0)
    player_background = (255, 255, 255) if current_player == 'w' else (0, 0, 0)
    current_player_button = pygame.Rect(BOARD_WIDTH + 20, 80, 40, 50)
    pygame.draw.rect(window, player_background, current_player_button)
    current_player_text = font.render(f"{'     White to move ' if current_player == 'w' else '     Black to move'}", True, player_color)
    window.blit(current_player_text, (BOARD_WIDTH + 30, 90))

    # Instructions
    instructions = [
        "",

        "How to Play:",
        "",

        "- Click and drag a piece to move it.",
        "- Press 'r' to restart.",
        "- Press 'u' to undo the last move.",
        "",
        "Special Moves:",
        "",

        "- Castling: Move the king",
        "  two squares.",
        "- Pawn Promotion: is now",
        "  available.",
    ]
    for i, line in enumerate(instructions):
        instruction_text = font.render(line, True, (0, 0, 0))
        window.blit(instruction_text, (BOARD_WIDTH + 20, 120 + 30 * i))

    # Best Move button
    draw_button(window, BEST_MOVE_BUTTON, "Best Move", font)

    # Resign button
    draw_button(window, RESIGN_BUTTON, "Resign", font)

    # Display Best Move
    if best_move_text:
        move_text = font.render(best_move_text, True, (0, 0, 0))
        window.blit(move_text, (BOARD_WIDTH + 20, HEIGHT - 150))


def handle_promotion(window, board, position):
    """Handle pawn promotion by prompting the player to choose a piece."""
    promotion = True
    chosen_piece = None
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 32)

    # Define promotion options
    options = ['Queen', 'Rook', 'Bishop', 'Knight']
    option_rects = []

    # Calculate button sizes and positions
    button_width, button_height = 150, 50
    spacing = 20
    total_width = 4 * button_width + 3 * spacing
    start_x = (WINDOW_WIDTH - total_width) // 2
    start_y = HEIGHT // 2 - button_height // 2

    for i, option in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_width + spacing), start_y, button_width, button_height)
        option_rects.append((option, rect))

    while promotion:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for option, rect in option_rects:
                    if rect.collidepoint(mouse_pos):
                        chosen_piece = option.lower()
                        promotion = False
                        break

        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, HEIGHT))
        overlay.set_alpha(180)  # Transparency
        overlay.fill((50, 50, 50))
        window.blit(overlay, (0, 0))

        # Draw promotion prompt
        prompt_text = font.render("Promote Pawn to:", True, (255, 255, 255))
        window.blit(prompt_text, (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, start_y - 60))

        # Draw promotion buttons
        for option, rect in option_rects:
            pygame.draw.rect(window, BUTTON_COLOR, rect)
            text = font.render(option, True, (255, 255, 255))
            window.blit(text, (
                rect.x + (rect.width - text.get_width()) // 2,
                rect.y + (rect.height - text.get_height()) // 2
            ))

        pygame.display.update()
        clock.tick(30)

    # Replace the pawn with the chosen piece
    row, col = position
    piece_images = load_images()  # Ensure images are loaded
    if chosen_piece == 'queen':
        board.board[row][col] = Queen(board.board[row][col].color, piece_images[f"{board.board[row][col].color}_queen"])
    elif chosen_piece == 'rook':
        board.board[row][col] = Rook(board.board[row][col].color, piece_images[f"{board.board[row][col].color}_rook"])
    elif chosen_piece == 'bishop':
        board.board[row][col] = Bishop(board.board[row][col].color, piece_images[f"{board.board[row][col].color}_bishop"])
    elif chosen_piece == 'knight':
        board.board[row][col] = Knight(board.board[row][col].color, piece_images[f"{board.board[row][col].color}_knight"])

    board.board[row][col].position = (row, col)
    board.board[row][col].has_moved = True

class Piece:
    def __init__(self, color, image, name):
        self.color = color
        self.image = image
        self.name = name
        self.position = None
        self.has_moved = False

    def get_potential_moves(self, position, board, for_attack=False):
        """Generate potential moves for the piece.
        
        Args:
            position (tuple): Current position (row, col) of the piece.
            board (Board): The current game board.
            for_attack (bool): If True, exclude special moves like castling.
        
        Returns:
            list: List of potential move positions (row, col).
        """
        return []

    def get_valid_moves(self, position, board):
        """Return a list of valid moves, ensuring the king is not left in check."""
        potential_moves = self.get_potential_moves(position, board, for_attack=False)
        valid_moves = []

        for move in potential_moves:
            # Simulate the move
            original_piece = board.get_piece(*move)
            original_position = self.position

            board.set_piece(move, self)
            board.set_piece(position, None)
            self.position = move

            # Check if move leaves the king in check
            if not board.is_in_check(self.color):
                valid_moves.append(move)

            # Undo the move
            board.set_piece(position, self)
            board.set_piece(move, original_piece)
            self.position = original_position

        return valid_moves

class Pawn(Piece):
    def __init__(self, color, image):
        name = 'P' if color == 'w' else 'p'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        direction = -1 if self.color == 'w' else 1
        row, col = position

        # Forward move
        if board.is_empty(row + direction, col):
            moves.append((row + direction, col))
            # Double move from starting position
            if (self.color == 'w' and row == 6) or (self.color == 'b' and row == 1):
                if board.is_empty(row + 2 * direction, col):
                    moves.append((row + 2 * direction, col))

        # Captures
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if 0 <= new_col < COLS and 0 <= new_row < ROWS:
                if board.is_enemy(new_row, new_col, self.color):
                    moves.append((new_row, new_col))
                # En passant can be added here in future

        # Promotion can be handled during move execution

        return moves

class Rook(Piece):
    def __init__(self, color, image):
        name = 'R' if color == 'w' else 'r'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        row, col = position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Vertical and horizontal directions

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < ROWS and 0 <= c < COLS:
                if board.is_empty(r, c):
                    moves.append((r, c))
                elif board.is_enemy(r, c, self.color):
                    moves.append((r, c))
                    break  # Stop if there's an enemy piece
                else:
                    break  # Stop if there's a friendly piece
                r += dr
                c += dc
        return moves

class Knight(Piece):
    def __init__(self, color, image):
        name = 'N' if color == 'w' else 'n'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        row, col = position
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2),  (1, 2),  (2, -1),  (2, 1)
        ]

        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                if board.is_empty(r, c) or board.is_enemy(r, c, self.color):
                    moves.append((r, c))
        return moves

class Bishop(Piece):
    def __init__(self, color, image):
        name = 'B' if color == 'w' else 'b'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        row, col = position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < ROWS and 0 <= c < COLS:
                if board.is_empty(r, c):
                    moves.append((r, c))
                elif board.is_enemy(r, c, self.color):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

class Queen(Piece):
    def __init__(self, color, image):
        name = 'Q' if color == 'w' else 'q'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        row, col = position
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),   # Rook-like moves
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop-like moves
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < ROWS and 0 <= c < COLS:
                if board.is_empty(r, c):
                    moves.append((r, c))
                elif board.is_enemy(r, c, self.color):
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

class King(Piece):
    def __init__(self, color, image):
        name = 'K' if color == 'w' else 'k'
        super().__init__(color, image, name)

    def get_potential_moves(self, position, board, for_attack=False):
        moves = []
        row, col = position
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                if board.is_empty(r, c) or board.is_enemy(r, c, self.color):
                    moves.append((r, c))

        if not self.has_moved and not board.is_in_check(self.color) and not for_attack:
            if self.can_castle_short(board):
                moves.append((row, col + 2))
            if self.can_castle_long(board):
                moves.append((row, col - 2))

        return moves
    
    def get_valid_moves(self, position, board):
        potential_moves = self.get_potential_moves(position, board)
        valid_moves = []
        for move in potential_moves:
            # Simulate the move
            original_piece = board.get_piece(*move)
            original_position = self.position

            board.set_piece(move, self)
            board.set_piece(position, None)
            self.position = move

            # Check if move leaves the king in check
            if not board.is_in_check(self.color):
                valid_moves.append(move)

            # Undo the move
            board.set_piece(position, self)
            board.set_piece(move, original_piece)
            self.position = original_position

        return valid_moves

    def can_castle_short(self, board):
        row = self.position[0]
        rook = board.get_piece(row, 7)
        if isinstance(rook, Rook) and not rook.has_moved:
            if board.is_empty(row, 5) and board.is_empty(row, 6):
                # Ensure squares are not under attack
                if not board.square_attacked((row, 5), self.color) and not board.square_attacked((row, 6), self.color):
                    return True
        return False

    def can_castle_long(self, board):
        row = self.position[0]
        rook = board.get_piece(row, 0)
        if isinstance(rook, Rook) and not rook.has_moved:
            if board.is_empty(row, 1) and board.is_empty(row, 2) and board.is_empty(row, 3):
                if not board.square_attacked((row, 2), self.color) and not board.square_attacked((row, 3), self.color):
                    return True
        return False

class Board:
    def __init__(self):
        self.board = []
        self.create_board()

    def create_board(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        for col in range(COLS):
            self.board[6][col] = Pawn('w', pieces_images['w_pawn'])
            self.board[6][col].position = (6, col)
            self.board[1][col] = Pawn('b', pieces_images['b_pawn'])
            self.board[1][col].position = (1, col)

        # Place other pieces
        placement = [
            ('w_rook', Rook), ('w_knight', Knight), ('w_bishop', Bishop),
            ('w_queen', Queen), ('w_king', King),
            ('w_bishop', Bishop), ('w_knight', Knight), ('w_rook', Rook)
        ]
        for col, (piece_name, piece_class) in enumerate(placement):
            self.board[7][col] = piece_class('w', pieces_images[piece_name])
            self.board[7][col].position = (7, col)

        placement = [
            ('b_rook', Rook), ('b_knight', Knight), ('b_bishop', Bishop),
            ('b_queen', Queen), ('b_king', King),
            ('b_bishop', Bishop), ('b_knight', Knight), ('b_rook', Rook)
        ]
        for col, (piece_name, piece_class) in enumerate(placement):
            self.board[0][col] = piece_class('b', pieces_images[piece_name])
            self.board[0][col].position = (0, col)

    def is_empty(self, row, col):
        """Check if a specific square is empty."""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col] is None
        return False

    def is_enemy(self, row, col, color):
        if 0 <= row < ROWS and 0 <= col < COLS:
            piece = self.board[row][col]
            return piece is not None and piece.color != color
        return False

    def move_piece(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.board[fr][fc]
        captured_piece = self.board[tr][tc]

        logging.debug(f"Moving {piece.name} from ({fr}, {fc}) to ({tr}, {tc})")
        if captured_piece:
            logging.debug(f"Captured {captured_piece.name} at ({tr}, {tc})")

        # Move the piece
        self.board[tr][tc] = piece
        self.board[fr][fc] = None
        piece.position = (tr, tc)
        piece.has_moved = True

        # Handle Castling
        if isinstance(piece, King):
            if tc - fc == 2:
                logging.debug("Performing short castling")
                self.move_rook((fr, 7), (fr, 5))
            elif tc - fc == -2:
                logging.debug("Performing long castling")
                self.move_rook((fr, 0), (fr, 3))

        # Check for pawn promotion
        promotion = False
        if isinstance(piece, Pawn):
            if (piece.color == 'w' and tr == 0) or (piece.color == 'b' and tr == 7):
                promotion = True

        return promotion, (tr, tc) if promotion else None

    def move_rook(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        rook = self.board[fr][fc]

        if rook is not None and isinstance(rook, Rook):
            self.board[tr][tc] = rook
            self.board[fr][fc] = None
            rook.position = (tr, tc)
            rook.has_moved = True

    def get_piece(self, row, col):
        return self.board[row][col] if 0 <= row < ROWS and 0 <= col < COLS else None

    def set_piece(self, position, piece):
        row, col = position
        self.board[row][col] = piece
        if piece:
            piece.position = position

    def is_in_check(self, color):
        king_position = self.find_king_position(color)
        if king_position is None:
            return False

        opponent_color = 'b' if color == 'w' else 'w'
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color and piece.name.lower() != 'k':  # Exclude King
                    potential_moves = piece.get_potential_moves((row, col), self, for_attack=True)
                    if king_position in potential_moves:
                        return True
        return False
    
    def find_king_position(self, color):
        """Find and return the king's position of the specified color."""
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return (row, col)  # Return the position as a tuple
        return None  # Return None if the king is not found

    def find_king(self, color):
        """Find and return the king's position of the specified color."""
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return piece  # Return the position as a tuple
        return None  # Return None if the king is not found

    def square_attacked(self, position, color):
        opponent_color = 'b' if color == 'w' else 'w'
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    potential_moves = piece.get_potential_moves((row, col), self, for_attack=True)
                    if position in potential_moves:
                        return True
        return False

    def get_fen(self):
        fen_rows = []
        for row in self.board:
            fen_row = ''
            empty_squares = 0
            for piece in row:
                if piece is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen_row += str(empty_squares)
                        empty_squares = 0
                    # Map piece names to standard FEN letters
                    # Ensure uppercase for white and lowercase for black
                    fen_piece = piece.name.upper() if piece.color == 'w' else piece.name.lower()
                    fen_row += fen_piece
            if empty_squares > 0:
                fen_row += str(empty_squares)
            fen_rows.append(fen_row)
        fen = '/'.join(fen_rows)
        
        # Active color
        fen += ' ' + ('w' if current_player == 'w' else 'b')
        
        # Castling availability
        castling = ''
        # White king
        white_king = self.find_king('w')
        if white_king and not white_king.has_moved:
            row, col = white_king.position
            # Check rooks
            rook = self.get_piece(7, 7)
            if isinstance(rook, Rook) and not rook.has_moved:
                castling += 'K'
            rook = self.get_piece(7, 0)
            if isinstance(rook, Rook) and not rook.has_moved:
                castling += 'Q'
        # Black king
        black_king = self.find_king('b')
        if black_king and not black_king.has_moved:
            row, col = black_king.position
            # Check rooks
            rook = self.get_piece(0, 7)
            if isinstance(rook, Rook) and not rook.has_moved:
                castling += 'k'
            rook = self.get_piece(0, 0)
            if isinstance(rook, Rook) and not rook.has_moved:
                castling += 'q'
        if castling == '':
            castling = '-'
        fen += ' ' + castling
        
        # En passant target square (always '-')
        fen += ' -'
        
        # Halfmove clock and fullmove number (set to defaults)
        fen += ' 0 1'
        
        return fen

def game_over_popup(winner):
    font = pygame.font.SysFont('Arial', 64)
    text_surface = font.render(f"{winner} Wins!", True, (255, 0, 0))
    WINDOW.fill((0, 0, 0))
    WINDOW.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)


def restart_game():
    global current_player, game_over, move_history
    board = Board()
    current_player = 'w'
    game_over = False
    move_history = []
    return board

def undo_last_move(board):
    global move_history
    global current_player

    if not move_history:
        print("No moves to undo.")
        return board

    last_moves = move_history.pop()

    # Ensure last_moves is a list
    if isinstance(last_moves, dict):
        last_moves = [last_moves]

    # Undo in reverse order to handle dependencies (e.g., king before rook)
    for move in reversed(last_moves):
        board.set_piece(move['from'], move['piece'])
        board.set_piece(move['to'], move['captured'])

        # If needed, handle additional state resets here
        if 'castle' in move:
            # Example: Reset castling rights if tracked
            move['piece'].has_moved = False
            pass

    # Toggle the player turn
    current_player = 'b' if current_player == 'w' else 'w'

    return board

def main():
    global current_player, game_over
    run = True
    clock = pygame.time.Clock()
    board = Board()
    best_move_text = ""

    dragging = False
    dragging_piece = None
    dragging_offset = (0, 0)
    valid_moves = []

    font = pygame.font.SysFont('Arial', 32)

    while run:
        clock.tick(60)
        draw_board(WINDOW)
        draw_pieces(WINDOW, board, exclude_piece=dragging_piece)

        if valid_moves:
            highlight_valid_moves(WINDOW, valid_moves)

        if dragging and dragging_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            WINDOW.blit(dragging_piece.image, (mouse_x - dragging_offset[0], mouse_y - dragging_offset[1]))

        if board.is_in_check(current_player):
            text_surface = font.render('Check!', True, (255, 0, 0))
            WINDOW.blit(text_surface, (BOARD_WIDTH // 2 - text_surface.get_width() // 2, 10))
        
        # Draw the instructions sidebar
        draw_instructions(WINDOW, font, current_player, best_move_text)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if BEST_MOVE_BUTTON.collidepoint(pos):
                    print("Best Move button clicked")
                    fen = board.get_fen()
                    print(f"FEN: {fen}")
                    try:
                        response = requests.get('https://lichess.org/api/cloud-eval', params={'fen': fen})
                        response.raise_for_status()
                        data = response.json()
                        if 'pvs' in data and len(data['pvs']) > 0:
                            best_pv = data['pvs'][0]
                            best_moves = best_pv['moves']
                            best_move = best_moves.split(' ')[0]
                            best_move_text = f"Best move: {best_move}"
                            print(f"Best move: {best_move}")
                        else:
                            best_move_text = "No best move found"
                            print("No best move found in response:", data)
                    except requests.exceptions.HTTPError as http_err:
                        best_move_text = f"HTTP error occurred: {http_err}"
                        print("HTTP error occurred:", http_err)
                        print("Response content:", response.content)
                    except Exception as err:
                        best_move_text = f"An error occurred: {err}"
                        print("An error occurred:", err)
                elif RESIGN_BUTTON.collidepoint(pos):
                    print("Resign button clicked")
                    game_over = True
                    game_over_popup(f"{'White' if current_player == 'b' else 'Black'} wins by resignation!")
                    board = restart_game()
                    best_move_text = ""


                row, col = get_row_col_from_mouse(pos)
                piece = board.get_piece(row, col)
                if piece and piece.color == current_player:
                    valid_moves = piece.get_valid_moves((row, col), board)
                    if not valid_moves:
                        continue
                    dragging = True
                    dragging_piece = piece
                    piece.position = (row, col)
                    piece_x = col * SQUARE_SIZE
                    piece_y = row * SQUARE_SIZE
                    dragging_offset = (pos[0] - piece_x, pos[1] - piece_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and dragging_piece:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    if (row, col) in valid_moves:
                        # Determine if the move is a castling move
                        is_castling = False
                        castle_type = None  # 'short' or 'long'
                        from_row, from_col = dragging_piece.position
                        to_row, to_col = row, col

                        if isinstance(dragging_piece, King) and abs(to_col - from_col) == 2:
                            is_castling = True
                            castle_type = 'short' if to_col - from_col == 2 else 'long'

                        if is_castling:
                            # Define rook movement based on castling type
                            if castle_type == 'short':
                                rook_from = (from_row, 7)
                                rook_to = (from_row, 5)
                            else:  # 'long'
                                rook_from = (from_row, 0)
                                rook_to = (from_row, 3)

                            # Get the rook piece
                            rook_piece = board.get_piece(*rook_from)

                            # Append both king and rook moves as a list
                            move_history.append([
                                {
                                    'from': (from_row, from_col),
                                    'to': (to_row, to_col),
                                    'piece': dragging_piece,
                                    'captured': board.get_piece(to_row, to_col)
                                },
                                {
                                    'from': rook_from,
                                    'to': rook_to,
                                    'piece': rook_piece,
                                    'captured': board.get_piece(*rook_to)
                                }
                            ])

                            # Perform the castling move
                            promotion, promotion_pos = board.move_piece((from_row, from_col), (to_row, to_col))
                        else:
                            # Regular move: append as a list with a single move dictionary
                            move_history.append([{
                                'from': dragging_piece.position,
                                'to': (row, col),
                                'piece': dragging_piece,
                                'captured': board.get_piece(row, col)
                            }])
                            promotion, promotion_pos = board.move_piece(dragging_piece.position, (row, col))

                        if is_castling:
                            # Handle castling promotion is not needed
                            pass
                        else:
                            # Check for pawn promotion
                            if promotion:
                                handle_promotion(WINDOW, board, promotion_pos)

                        # Reset best move text
                        best_move_text = ""

                        # Check for game over conditions
                        opponent_color = 'b' if current_player == 'w' else 'w'
                        opponent_has_moves = False
                        for r in range(ROWS):
                            for c in range(COLS):
                                piece = board.get_piece(r, c)
                                if piece and piece.color == opponent_color:
                                    if piece.get_valid_moves((r, c), board):
                                        opponent_has_moves = True
                                        break
                            if opponent_has_moves:
                                break
                        if not opponent_has_moves:
                            if board.is_in_check(opponent_color):
                                if current_player == "w":
                                    game_over_popup("White")
                                    board = restart_game()
                                else:
                                    game_over_popup("Black")
                                    board = restart_game()
                            else:
                                game_over_popup("Draw")
                                board = restart_game()

                            game_over = True
                        else:
                            current_player = opponent_color
                    dragging_piece = None
                    dragging = False
                    valid_moves = []

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = restart_game()
                    best_move_text = ""
                elif event.key == pygame.K_u:
                    board = undo_last_move(board)
                    best_move_text = ""

    pygame.quit()

if __name__ == "__main__":
    pieces_images = load_images()
    if not pieces_images:
        print("Failed to load piece images. Please check the URLs.")
    else:
        main()
