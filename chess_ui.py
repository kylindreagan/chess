# chess_gui.py
import pygame as p
from chess_engine import GameState, Move

# Increased window width to accommodate sidebar
BOARD_WIDTH = BOARD_HEIGHT = 512
SIDEBAR_WIDTH = 200
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH
HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))

def show_menu():
    p.init()
    # Create a separate window for the menu
    menu_width = 400
    menu_height = 500
    menu_screen = p.display.set_mode((menu_width, menu_height))
    p.display.set_caption("Chess - Select Mode")
    
    menu_font = p.font.SysFont("helvetica", 40, True, False)
    title_font = p.font.SysFont("helvetica", 60, True, False)
    small_font = p.font.SysFont("helvetica", 20, False, False)
    
    one_player_button = p.Rect(menu_width//2 - 100, menu_height//2 - 50, 200, 60)
    two_player_button = p.Rect(menu_width//2 - 100, menu_height//2 + 50, 200, 60)
    
    # Timer toggle
    timer_toggle_rect = p.Rect(menu_width//2 - 100, menu_height//2 + 130, 200, 40)
    timer_enabled = False
    
    menu_running = True
    selected_mode = None
    
    while menu_running:
        menu_screen.fill(p.Color("white"))
        
        # Draw title
        title_text = title_font.render("CHESS", 0, p.Color("black"))
        menu_screen.blit(title_text, (menu_width//2 - title_text.get_width()//2, menu_height//4 - 50))
        
        # Draw buttons
        p.draw.rect(menu_screen, p.Color("lightblue"), one_player_button)
        p.draw.rect(menu_screen, p.Color("lightgreen"), two_player_button)
        
        p.draw.rect(menu_screen, p.Color("black"), one_player_button, 3)
        p.draw.rect(menu_screen, p.Color("black"), two_player_button, 3)
        
        # Draw button text
        one_player_text = menu_font.render("1 Player", 0, p.Color("black"))
        two_player_text = menu_font.render("2 Players", 0, p.Color("black"))
        
        menu_screen.blit(one_player_text, (one_player_button.centerx - one_player_text.get_width()//2, 
                                         one_player_button.centery - one_player_text.get_height()//2))
        menu_screen.blit(two_player_text, (two_player_button.centerx - two_player_text.get_width()//2, 
                                         two_player_button.centery - two_player_text.get_height()//2))
        
        # Draw timer toggle
        toggle_color = p.Color("green") if timer_enabled else p.Color("red")
        p.draw.rect(menu_screen, toggle_color, timer_toggle_rect)
        p.draw.rect(menu_screen, p.Color("black"), timer_toggle_rect, 2)
        
        timer_text = small_font.render("Move Timer: ON" if timer_enabled else "Move Timer: OFF", 0, p.Color("white"))
        menu_screen.blit(timer_text, (timer_toggle_rect.centerx - timer_text.get_width()//2, 
                                    timer_toggle_rect.centery - timer_text.get_height()//2))
        
        # Draw instructions
        instruction_text = small_font.render("Select game mode", 0, p.Color("gray"))
        menu_screen.blit(instruction_text, (menu_width//2 - instruction_text.get_width()//2, menu_height//2 - 100))
        
        timer_instruction = small_font.render("Click to toggle move timer", 0, p.Color("gray"))
        menu_screen.blit(timer_instruction, (menu_width//2 - timer_instruction.get_width()//2, menu_height//2 + 175))
        
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                return None, False
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                if one_player_button.collidepoint(mouse_pos):
                    selected_mode = "1p"
                    menu_running = False
                elif two_player_button.collidepoint(mouse_pos):
                    selected_mode = "2p"
                    menu_running = False
                elif timer_toggle_rect.collidepoint(mouse_pos):
                    timer_enabled = not timer_enabled
        
        p.display.flip()
    
    p.quit()  # Close the menu window completely
    return selected_mode, timer_enabled

class Timer:
    def __init__(self, time_limit=600):
        self.time_limit = time_limit  # seconds per move
        self.white_time = time_limit
        self.black_time = time_limit
        self.white_start_time = None
        self.black_start_time = None
        self.active_color = None
        
    def start_turn(self, white_to_move):
        if white_to_move:
            self.white_start_time = p.time.get_ticks()
        else:
            self.black_start_time = p.time.get_ticks()
        self.active_color = 'white' if white_to_move else 'black'
        
    def update_times(self, white_to_move):
        current_time = p.time.get_ticks()
        if self.active_color == 'white' and self.white_start_time is not None:
            elapsed = (current_time - self.white_start_time) // 1000
            self.white_time = max(0, self.white_time - elapsed)
            self.white_start_time = current_time
        elif self.active_color == 'black' and self.black_start_time is not None:
            elapsed = (current_time - self.black_start_time) // 1000
            self.black_time = max(0, self.black_time - elapsed)
            self.black_start_time = current_time
            
    def switch_turn(self, white_to_move):
        self.update_times(white_to_move)
        self.start_turn(white_to_move)
        
    def reset(self):
        self.white_time = self.time_limit
        self.black_time = self.time_limit
        self.white_start_time = None
        self.black_start_time = None
        self.active_color = None
        
    def is_time_up(self, white_to_move):
        if white_to_move:
            return self.white_time <= 0
        else:
            return self.black_time <= 0
            
    def get_formatted_time(self, white_to_move):
        if white_to_move:
            minutes = self.white_time // 60
            seconds = self.white_time % 60
        else:
            minutes = self.black_time // 60
            seconds = self.black_time % 60
        return f"{minutes:02d}:{seconds:02d}"

def run_game(game_mode, timer_enabled):
    # Initialize pygame for the game window
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess Game")
    clock = p.time.Clock()
    
    # Initialize game
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    move_made = False
    game_over = False
    player_one = True  # Human plays white
    player_two = (game_mode == "2p")  # Human plays black in 2p mode, bot plays black in 1p mode
    
    # Initialize timer
    move_timer = Timer()
    last_time_update = p.time.get_ticks()
    time_out = False

    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        
        # Update timer if enabled
        if timer_enabled and not game_over and not time_out:
            current_time = p.time.get_ticks()
            if current_time - last_time_update >= 1000:  # Update every second
                move_timer.update_times(gs.white_to_move)
                last_time_update = current_time
                
                # Check for timeout
                if move_timer.is_time_up(gs.white_to_move):
                    time_out = True
                    game_over = True
        
        # Start timer for new turn
        if timer_enabled and move_timer.active_color is None and not game_over:
            move_timer.start_turn(gs.white_to_move)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                return "quit"
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and not time_out and human_turn:
                    location = p.mouse.get_pos()
                    # Only process clicks on the board area (not sidebar)
                    if location[0] < BOARD_WIDTH:
                        col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
                        if sq_selected == (row, col):
                            sq_selected = ()
                            player_clicks = []
                        else:
                            sq_selected = (row, col)
                            player_clicks.append(sq_selected)
                        if len(player_clicks) == 2:
                            move = Move(player_clicks[0], player_clicks[1], gs.board)
                            for valid_move in valid_moves:
                                if move == valid_move:
                                    gs.make_move(valid_move)
                                    move_made = True
                                    sq_selected = ()
                                    player_clicks = []
                                    # Switch timer to next player
                                    if timer_enabled:
                                        move_timer.switch_turn(gs.white_to_move)
                                    break
                            if not move_made:
                                player_clicks = [sq_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    game_over = False
                    time_out = False
                    # Reset timer on undo
                    if timer_enabled:
                        move_timer.reset()
                        move_timer.start_turn(gs.white_to_move)
                elif e.key == p.K_t:
                    # Toggle timer during game
                    timer_enabled = not timer_enabled
                    if timer_enabled:
                        move_timer.reset()
                        move_timer.start_turn(gs.white_to_move)
                    else:
                        move_timer.reset()
                elif e.key == p.K_ESCAPE:
                    return "main_menu"

        # AI move finder logic (for 1p mode)
        if not game_over and not time_out and not human_turn and game_mode == "1p":
            # TODO: Add your bot logic here
            # For now, we'll just make a random valid move
            import random
            if valid_moves:
                ai_move = random.choice(valid_moves)
                gs.make_move(ai_move)
                move_made = True
                # Switch timer to next player
                if timer_enabled:
                    move_timer.switch_turn(gs.white_to_move)

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        # Draw everything
        screen.fill(p.Color("gray"))  # Background for sidebar
        
        # Draw board area
        draw_game_state(screen, gs, valid_moves, sq_selected)
        
        # Draw sidebar with all UI elements
        draw_sidebar(screen, game_mode, gs, timer_enabled, move_timer)
        
        # Draw game over messages (on top of everything)
        winner_text = ""
        if time_out:
            winner_text = "Black wins on time!" if gs.white_to_move else "White wins on time!"
            draw_text(screen, winner_text)
        elif gs.checkmate:
            game_over = True
            winner_text = "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_text(screen, winner_text)
        elif gs.stalemate:
            game_over = True
            winner_text = "Stalemate"
            draw_text(screen, winner_text)

        clock.tick(MAX_FPS)
        p.display.flip()
    
    p.quit()
    return "main_menu"

def draw_game_state(screen, gs, valid_moves, sq_selected):
    # Only draw on the board area (left side)
    board_surface = p.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    draw_board(board_surface)
    highlight_squares(board_surface, gs, valid_moves, sq_selected)
    draw_pieces(board_surface, gs.board)
    highlight_king_in_check(board_surface, gs)
    screen.blit(board_surface, (0, 0))

def draw_sidebar(screen, game_mode, gs, timer_enabled, move_timer):
    sidebar_x = BOARD_WIDTH + 10
    
    # Sidebar background
    sidebar_bg = p.Surface((SIDEBAR_WIDTH - 20, HEIGHT - 20))
    sidebar_bg.fill(p.Color("lightgray"))
    screen.blit(sidebar_bg, (sidebar_x, 10))
    
    # Game info
    info_font = p.font.SysFont("helvetica", 18, True, False)
    small_font = p.font.SysFont("helvetica", 16, False, False)
    
    # Game mode
    mode_text = f"Game Mode: {'1 Player vs AI' if game_mode == '1p' else '2 Players'}"
    mode_surface = info_font.render(mode_text, True, p.Color("black"))
    screen.blit(mode_surface, (sidebar_x + 10, 20))
    
    # Current turn
    turn_text = f"Current Turn: {'White' if gs.white_to_move else 'Black'}"
    turn_surface = info_font.render(turn_text, True, p.Color("black"))
    screen.blit(turn_surface, (sidebar_x + 10, 50))
    
    # Timer status
    timer_status = "Timer: ENABLED" if timer_enabled else "Timer: DISABLED"
    timer_status_surface = info_font.render(timer_status, True, p.Color("green") if timer_enabled else p.Color("red"))
    screen.blit(timer_status_surface, (sidebar_x + 10, 80))
    
    # Timer displays
    if timer_enabled:
        # White timer
        white_time_text = f"White: {move_timer.get_formatted_time(True)}"
        white_surface = small_font.render(white_time_text, True, p.Color("black"))
        screen.blit(white_surface, (sidebar_x + 10, 120))
        
        # Black timer  
        black_time_text = f"Black: {move_timer.get_formatted_time(False)}"
        black_surface = small_font.render(black_time_text, True, p.Color("black"))
        screen.blit(black_surface, (sidebar_x + 10, 150))
        
        # Highlight active timer
        if gs.white_to_move:
            p.draw.rect(screen, p.Color("yellow"), (sidebar_x + 5, 115, SIDEBAR_WIDTH - 30, 25), 2)
        else:
            p.draw.rect(screen, p.Color("yellow"), (sidebar_x + 5, 145, SIDEBAR_WIDTH - 30, 25), 2)
    
    # Controls section
    controls_y = 200
    controls_title = info_font.render("Controls:", True, p.Color("darkblue"))
    screen.blit(controls_title, (sidebar_x + 10, controls_y))
    
    controls = [
        "Z - Undo move",
        "T - Toggle timer", 
        "ESC - Main menu",
        "Click - Select/move"
    ]
    
    for i, control in enumerate(controls):
        control_surface = small_font.render(control, True, p.Color("black"))
        screen.blit(control_surface, (sidebar_x + 20, controls_y + 30 + i * 25))
    
    # Game state info
    state_y = controls_y + 150
    if gs.in_check():
        check_text = "CHECK!"
        check_surface = info_font.render(check_text, True, p.Color("red"))
        screen.blit(check_surface, (sidebar_x + 10, state_y))
    
    # Move count
    move_text = f"Moves: {len(gs.move_log)}"
    move_surface = small_font.render(move_text, True, p.Color("black"))
    screen.blit(move_surface, (sidebar_x + 10, state_y + 30))

def draw_board(screen):
    colors = [p.Color("burlywood1"), p.Color("saddlebrown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        piece = gs.board[r][c]
        if piece != "--" and ((piece[0] == 'w' and gs.white_to_move) or (piece[0] == 'b' and not gs.white_to_move)):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color("green"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))

def highlight_king_in_check(screen, gs):
    if gs.in_check():
        king_pos = gs.find_king('w' if gs.white_to_move else 'b')
        if king_pos:
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color("red"))
            screen.blit(s, (king_pos[1] * SQ_SIZE, king_pos[0] * SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_text(screen, text):
    # Create a semi-transparent background for the text
    font = p.font.SysFont("helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("red"))
    
    # Create background for text
    text_bg = p.Surface((text_object.get_width() + 20, text_object.get_height() + 20), p.SRCALPHA)
    text_bg.fill((0, 0, 0, 150))  # Dark semi-transparent background
    text_bg_rect = text_bg.get_rect(center=(BOARD_WIDTH//2, BOARD_HEIGHT//2))
    
    screen.blit(text_bg, text_bg_rect)
    screen.blit(text_object, (BOARD_WIDTH//2 - text_object.get_width()//2, BOARD_HEIGHT//2 - text_object.get_height()//2))

def main():
    while True:
        # Show menu first
        game_mode, timer_enabled = show_menu()
        if game_mode is None:
            break
        
        # Run the game
        result = run_game(game_mode, timer_enabled)
        
        if result == "quit":
            break

if __name__ == "__main__":
    main()