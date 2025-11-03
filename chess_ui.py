# chess_gui.py
import pygame as p
from chess_engine import GameState, Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    move_made = False
    game_over = False

    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col,row = location[0]//SQ_SIZE, location[1]//SQ_SIZE
                    if sq_selected==(row,col):
                        sq_selected=()
                        player_clicks=[]
                    else:
                        sq_selected=(row,col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks)==2:
                        move = Move(player_clicks[0],player_clicks[1],gs.board)
                        for valid_move in valid_moves:
                            if move==valid_move:
                                gs.make_move(valid_move)
                                move_made=True
                                sq_selected=()
                                player_clicks=[]
                                break
                        if not move_made:
                            player_clicks=[sq_selected]
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z:
                    gs.undo_move()
                    move_made=True
                    game_over=False

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made=False

        draw_game_state(screen,gs,valid_moves,sq_selected)

        if gs.checkmate:
            game_over=True
            draw_text(screen,"Black wins" if gs.white_to_move else "White wins by checkmate")
        elif gs.stalemate:
            game_over=True
            draw_text(screen,"Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen,gs,valid_moves,sq_selected):
    draw_board(screen)
    highlight_squares(screen,gs,valid_moves,sq_selected)
    draw_pieces(screen,gs.board)
    highlight_king_in_check(screen,gs)

def draw_board(screen):
    colors=[p.Color("burlywood1"),p.Color("saddlebrown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def highlight_squares(screen,gs,valid_moves,sq_selected):
    if sq_selected!=():
        r,c=sq_selected
        piece=gs.board[r][c]
        if piece!="--" and ((piece[0]=='w' and gs.white_to_move) or (piece[0]=='b' and not gs.white_to_move)):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color("green"))
            for move in valid_moves:
                if move.start_row==r and move.start_col==c:
                    screen.blit(s,(move.end_col*SQ_SIZE,move.end_row*SQ_SIZE))

def highlight_king_in_check(screen,gs):
    if gs.in_check():
        king_pos = gs.find_king('w' if gs.white_to_move else 'b')
        if king_pos:
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color("red"))
            screen.blit(s,(king_pos[1]*SQ_SIZE,king_pos[0]*SQ_SIZE))

def draw_pieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def draw_text(screen,text):
    font=p.font.SysFont("helvetica",32,True,False)
    text_object=font.render(text,0,p.Color("red"))
    text_location = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object,text_location)

if __name__=="__main__":
    main()