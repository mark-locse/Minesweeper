import pygame
import sys
import os
from Minesweeper_Logic import Game, GameState
from enum import Enum, auto

SCREEN_W = 800
SCREEN_H = 700
MENU_W = 200
MENU_H = 60
MIN_CELL_SIZE = 18
MAX_CELL_SIZE = 40
HEADER = 75
PADDING = 20
RESTART_W = 120
RESTART_H = 40

class AppState(Enum):
    MENU = auto()
    CONTROLS = auto()
    GAME = auto()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)

def get_layout(screen):
    w = screen.get_width()
    return {
        "btn_rect": pygame.Rect((w - RESTART_W) // 2,(HEADER - RESTART_H) // 2,RESTART_W,RESTART_H),
        "left": pygame.Rect(10,15,120,45),
        "center": pygame.Rect((w//2)-25, 15, 50, 45),
        "right": pygame.Rect(w-130, 15, 120, 45)
    }

def get_menu_layout(screen):
    w, h = screen.get_size()
    return {
        "start": pygame.Rect((w - MENU_W)//2, h//2 - 80, MENU_W, MENU_H),
        "difficulty": pygame.Rect((w - MENU_W)//2, h//2, MENU_W, MENU_H),
        "controls": pygame.Rect((w - MENU_W)//2, h//2 + 80, MENU_W, MENU_H),
        "quit": pygame.Rect((w- MENU_W)//2, h//2 + 160, MENU_W, MENU_H),
    }

def handle_menu_click(pos, layout, difficulty):
    x, y = pos

    if layout["start"].collidepoint(x,y):
        return "start", difficulty

    if layout["difficulty"].collidepoint(x,y):
        # simple cycle
        order = ["beginner", "intermediate", "expert", "impossible"]
        next_index = (order.index(difficulty) + 1) % len(order)
        return "difficulty", order[next_index]
    if layout["controls"].collidepoint(x,y):
        return "controls", difficulty
    if layout["quit"].collidepoint(x,y):
        return "quit", difficulty
    return None, difficulty

def compute_cell_size(grid_w, grid_h, screen_w, screen_h):
    usable_w = screen_w - 2*PADDING
    usable_h = screen_h - HEADER - 2*PADDING
    cell_w = usable_w//grid_w
    cell_h = usable_h//grid_h
    return max(MIN_CELL_SIZE, min(MAX_CELL_SIZE, cell_w, cell_h))

#icons
def load_icons(CELL_SIZE):
    mine_size = int(CELL_SIZE * 0.8)
    flag_size = int(CELL_SIZE * 0.7)
                        
    return {
        "happy": pygame.transform.smoothscale(pygame.image.load(resource_path("Icons/Happy.png")).convert_alpha(), (40,40)),
        "win": pygame.transform.smoothscale(pygame.image.load(resource_path("Icons/Win.png")).convert_alpha(), (40,40)),
        "lose": pygame.transform.smoothscale(pygame.image.load(resource_path("Icons/Loss.png")).convert_alpha(), (40,40)),
        "mine": pygame.transform.smoothscale(pygame.image.load(resource_path("Icons/Mine.png")).convert_alpha(), (mine_size,mine_size)),
        "flag": pygame.transform.smoothscale(pygame.image.load(resource_path("Icons/Flag.png")).convert_alpha(), (flag_size,flag_size)),
    }

def condition_check(game, condition):
    if condition == "Won":
        game.state = GameState.WON
    elif condition == "Lost":
        game.state = GameState.LOST
    return

def button_highlight(rect, mouse):
    return (220,220,220) if rect.collidepoint(mouse) else (180,180,180)

def main():
    #Initialising
    pygame.init()
    font = pygame.font.Font(resource_path("Fonts/Minesweeper.ttf"), 20)
    big_font = pygame.font.Font(resource_path("Fonts/Minesweeper.ttf"), 36)
    small_font = pygame.font.Font(resource_path("Fonts/Minesweeper.ttf"), 14)
    
    screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
    
    logo = pygame.image.load(resource_path("Icons/Logo.png")).convert_alpha()
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Minesweeper")

    #timer
    clock = pygame.time.Clock()
    
   
    difficulty = "beginner"
    app_state = AppState.MENU
    running = True
    while running:

        #MENU State Event Handler
        if app_state == AppState.MENU:
            layout = get_menu_layout(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    action, difficulty = handle_menu_click(event.pos, layout, difficulty)

                    if action == "start":
                        game = Game(difficulty)
                        CELL_SIZE = compute_cell_size(
                            game.grid.width,
                            game.grid.height,
                            SCREEN_W,
                            SCREEN_H
                        )
                    
                        board_w = game.grid.width * CELL_SIZE
                        board_h = game.grid.height * CELL_SIZE
                        available_h = SCREEN_H - HEADER - PADDING * 2
                        board_x = (SCREEN_W - board_w) // 2
                        board_y = HEADER + (available_h - board_h) // 2

                        icons = load_icons(CELL_SIZE)
                        
                        start_time = 0
                        elapsed_time = 0

                        app_state = AppState.GAME

                    elif action == "controls":
                        app_state = AppState.CONTROLS

                    elif action == "quit":
                        running = False

            draw_menu(screen, font, big_font, small_font, layout, difficulty)    

        elif app_state == AppState.CONTROLS:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    app_state = AppState.MENU

            draw_controls(screen, big_font)
        
        # GAME State Event Handler
        elif app_state == AppState.GAME:
            layout = get_layout(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    if mouse_y < HEADER:
                        if layout["center"].collidepoint(mouse_x, mouse_y):
                            game = Game(difficulty)
                            start_time = 0
                            elapsed_time = 0
                            game.state = GameState.READY
                        continue
                    
                    grid_x = (mouse_x - board_x) // CELL_SIZE
                    grid_y = (mouse_y - board_y) // CELL_SIZE
                    if not (0 <= grid_x < game.grid.width and 0 <= grid_y < game.grid.height):
                        continue

                    if event.button == 1:
                        if game.state == GameState.READY:
                            game.state = GameState.RUNNING
                            start_time = pygame.time.get_ticks()

                        if game.state in (GameState.LOST, GameState.WON):
                            continue

                        cell = game.grid.cells[grid_y][grid_x]
                        if cell.revealed:
                            condition = game.grid.chord(grid_x, grid_y)
                        else:
                            condition = game.grid.reveal(grid_x, grid_y)

                        condition_check(game, condition)
                        
                    elif event.button == 3:
                        if game.state not in (GameState.LOST, GameState.WON):
                            game.grid.toggle_flag(grid_x, grid_y)
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Game(difficulty)
                        start_time = 0
                        elapsed_time = 0
                        game.state = GameState.READY
                    elif event.key == pygame.K_ESCAPE:
                        app_state = AppState.MENU
                        start_time = 0
                        elapsed_time = 0

            if game.state == GameState.RUNNING:
                elapsed_time = (pygame.time.get_ticks() - start_time)//1000

            #Draw
            screen.fill((150,150,150))
            draw_header(screen, game, font, layout, icons, elapsed_time)
            draw_grid(screen, game, font, board_x, board_y, icons, CELL_SIZE)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()



def draw_menu(screen, font, big_font, small_font, layout, difficulty):
    screen.fill((30,30,30))
    mouse = pygame.mouse.get_pos()
    for name, rect in layout.items():
            pygame.draw.rect(screen, button_highlight(rect, mouse), rect)
            pygame.draw.rect(screen, (0,0,0), rect, 2)

    title = big_font.render("MINESWEEPER", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, 120)))

    start_txt = font.render("START", True, (0, 0, 0))
    screen.blit(start_txt, start_txt.get_rect(center=layout["start"].center))

    diff_txt = small_font.render(f"DIFFICULTY: {difficulty}", True, (0, 0, 0))
    screen.blit(diff_txt, diff_txt.get_rect(center=layout["difficulty"].center))

    controls_txt = font.render("CONTROLS", True, (0,0,0))
    screen.blit(controls_txt, controls_txt.get_rect(center=layout["controls"].center))
    
    quit_txt = font.render("QUIT", True, (0, 0, 0))
    screen.blit(quit_txt, quit_txt.get_rect(center=layout["quit"].center))

def draw_controls(screen, big_font):
    screen.fill((30,30,30))
    font = big_font
    lines = [
        "Left Click: Reveal",
        "Left Click (If Revealed): Chord",
        "Right Click: Flag",
        "ESC: Return to Main Menu",
        "R: Restart Game"
    ]

    w = screen.get_width()
    
    for i, text in enumerate(lines):
        surf = font.render(text, True, (255,255,255))
        rect = surf.get_rect(center=(w//2,120+i*40))
        screen.blit(surf, rect)

def draw_header(screen, game, font, layout, icons, elapsed_time):
    w = screen.get_width()
    left = layout["left"]
    center = layout["center"]
    right = layout["right"]
    pygame.draw.rect(screen, (200,200,200), (0,0,w,HEADER))

    #Remaining Mines Counter
    pygame.draw.rect(screen, (180,180,180), left)
    pygame.draw.rect(screen, (0,0,0), left, 2)
    flags = sum(cell.flagged for row in game.grid.cells for cell in row)
    mines = font.render(str(game.grid.mines-flags), True, (0,0,0))
    screen.blit(mines, mines.get_rect(center=left.center))

    #Icon (Also acts as Restart)
    pygame.draw.rect(screen,(180,180,180), center)
    pygame.draw.rect(screen, (0,0,0), center, 2)
    if game.state == GameState.LOST:
        symbol = icons["lose"]
    elif game.state == GameState.WON:
        symbol = icons["win"]
    else:
        symbol = icons["happy"]
    screen.blit(symbol, symbol.get_rect(center=center.center))

    #Timer
    pygame.draw.rect(screen, (180,180,180), right)
    pygame.draw.rect(screen, (0,0,0), right, 2)
    timer = font.render(f"{elapsed_time:03}", True, (0,0,0))
    screen.blit(timer, timer.get_rect(center=right.center))


def draw_grid(screen, game, font, board_x, board_y, icons, CELL_SIZE):
    grid = game.grid
    NUMBER_COLOURS = {
        1: (0, 0, 255),
        2: (0, 128, 0),
        3: (255, 0, 0),
        4: (0, 0, 128),
        5: (128, 0, 0),
        6: (0, 128, 128),
        7: (0, 0, 0),
        8: (128, 128, 128)
    }
    
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            rect = pygame.Rect(
                board_x + x*CELL_SIZE,
                board_y + y*CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )               
                
            if cell.revealed:
                pygame.draw.rect(screen, (200,200,200), rect)
                if cell.adjacent > 0:
                    colour = NUMBER_COLOURS[cell.adjacent]
                    text = font.render(str(cell.adjacent), True, colour)
                    text_rect = text.get_rect(center = rect.center)
                    screen.blit(text,text_rect)
            else:
                pygame.draw.rect(screen, (120,120,120), rect)

            show_mine = (cell.is_mine and (cell.revealed or game.state == GameState.LOST))
            if show_mine and not cell.flagged:
                symbol = icons["mine"]
                screen.blit(symbol, symbol.get_rect(center=rect.center))

            pygame.draw.rect(screen, (60,60,60), rect, 1)
            
            if cell.flagged:
                symbol = icons["flag"]
                screen.blit(symbol, symbol.get_rect(center=rect.center))

    grid_rect = pygame.Rect(
        board_x,
        board_y,
        game.grid.width * CELL_SIZE,
        game.grid.height * CELL_SIZE,
    )
    pygame.draw.rect(screen, (30,30,30), grid_rect, 4)
    

if __name__ == "__main__":
    main()
