import pygame, sys, time, os, random

pygame.init()

# ---------------- Window setup ----------------
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tic Tac Toe")

# ---------------- Colors ----------------
BG_COLOR      = (28, 170, 156)
LINE_COLOR    = (23, 145, 135)
CIRCLE_COLOR  = (239, 231, 200)
CROSS_COLOR   = (66, 66, 66)
TEXT_COLOR    = (255, 255, 255)

# ---------------- Board setup ----------------
BOARD_ROWS, BOARD_COLS = 3, 3
board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

# ---------------- Media Path Setup ----------------
BASE_PATH  = os.path.dirname(os.path.abspath(__file__))
bg_path    = os.path.join(BASE_PATH, "bg.png")
music_path = os.path.join(BASE_PATH, "music.mp3")

# Background image
bg_image = None
if os.path.exists(bg_path):
    try:
        bg_image = pygame.image.load(bg_path).convert()
    except Exception:
        bg_image = None

# Music
music_playing = False
if os.path.exists(music_path):
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # loop
        music_playing = True
    except Exception:
        music_playing = False

# ---------------- Dynamic sizes ----------------
def update_sizes():
    global BOARD_SIZE, BOARD_LEFT, BOARD_TOP
    global SQUARE_SIZE, CIRCLE_RADIUS, CIRCLE_WIDTH, CROSS_WIDTH, SPACE

    BOARD_SIZE  = min(WIDTH, HEIGHT)
    BOARD_LEFT  = (WIDTH  - BOARD_SIZE) // 2
    BOARD_TOP   = (HEIGHT - BOARD_SIZE) // 2

    SQUARE_SIZE   = BOARD_SIZE // BOARD_COLS
    CIRCLE_RADIUS = SQUARE_SIZE // 3
    CIRCLE_WIDTH  = 15
    CROSS_WIDTH   = 25
    SPACE         = SQUARE_SIZE // 4

update_sizes()

# ---------------- Game variables ----------------
player = 'X'
player_symbol, cpu_symbol = 'X', 'O'
game_over, winner = False, None
mode = None   # "pvp" or "cpu"
title_font  = pygame.font.SysFont(None, 64)
button_font = pygame.font.SysFont(None, 40)
small_font  = pygame.font.SysFont(None, 24)
font        = pygame.font.SysFont(None, 48)  # timer font
timer_start = None

# ---------------- Screen states ----------------
on_start_screen   = True
on_symbol_select  = False
on_restart_screen = False

# ---------------- Utility: draw background ----------------
def draw_background():
    if bg_image:
        screen.blit(pygame.transform.scale(bg_image, (WIDTH, HEIGHT)), (0, 0))
    else:
        screen.fill(BG_COLOR)

# ---------------- Drawing board & figures ----------------
def draw_lines():
    # grid lines over background
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(
            screen, LINE_COLOR,
            (BOARD_LEFT, BOARD_TOP + i * SQUARE_SIZE),
            (BOARD_LEFT + BOARD_SIZE, BOARD_TOP + i * SQUARE_SIZE), 5
        )
    for j in range(1, BOARD_COLS):
        pygame.draw.line(
            screen, LINE_COLOR,
            (BOARD_LEFT + j * SQUARE_SIZE, BOARD_TOP),
            (BOARD_LEFT + j * SQUARE_SIZE, BOARD_TOP + BOARD_SIZE), 5
        )

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            cx = BOARD_LEFT + col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = BOARD_TOP + row * SQUARE_SIZE + SQUARE_SIZE // 2
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, (cx, cy), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                pygame.draw.line(
                    screen, CROSS_COLOR,
                    (BOARD_LEFT + col * SQUARE_SIZE + SPACE,
                     BOARD_TOP + row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    (BOARD_LEFT + col * SQUARE_SIZE + SQUARE_SIZE - SPACE,
                     BOARD_TOP + row * SQUARE_SIZE + SPACE),
                    CROSS_WIDTH
                )
                pygame.draw.line(
                    screen, CROSS_COLOR,
                    (BOARD_LEFT + col * SQUARE_SIZE + SPACE,
                     BOARD_TOP + row * SQUARE_SIZE + SPACE),
                    (BOARD_LEFT + col * SQUARE_SIZE + SQUARE_SIZE - SPACE,
                     BOARD_TOP + row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                    CROSS_WIDTH
                )

# ---------------- Game logic helpers ----------------
def check_winner(b=None):
    if b is None:
        b = board
    # rows
    for row in b:
        if row[0] == row[1] == row[2] != '':
            return row[0]
    # cols
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] != '':
            return b[0][col]
    # diagonals
    if b[0][0] == b[1][1] == b[2][2] != '':
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != '':
        return b[0][2]
    return None

def is_full(b=None):
    if b is None:
        b = board
    return all(b[r][c] != '' for r in range(BOARD_ROWS) for c in range(BOARD_COLS))

def restart_game():
    global board, player, game_over, winner, timer_start
    board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    player = 'X'
    game_over, winner = False, None
    timer_start = time.time()

# ---------------- Minimax AI ----------------
def minimax(b, depth, is_maximizing):
    win = check_winner(b)
    if win == cpu_symbol:
        return 10 - depth
    elif win == player_symbol:
        return depth - 10
    elif is_full(b):
        return 0

    if is_maximizing:
        best = -100
        for r in range(3):
            for c in range(3):
                if b[r][c] == '':
                    b[r][c] = cpu_symbol
                    score = minimax(b, depth + 1, False)
                    b[r][c] = ''
                    best = max(best, score)
        return best
    else:
        best = 100
        for r in range(3):
            for c in range(3):
                if b[r][c] == '':
                    b[r][c] = player_symbol
                    score = minimax(b, depth + 1, True)
                    b[r][c] = ''
                    best = min(best, score)
        return best

def cpu_move():
    best_score = -100
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == '':
                board[r][c] = cpu_symbol
                score = minimax(board, 0, False)
                board[r][c] = ''
                if score > best_score:
                    best_score = score
                    move = (r, c)
    if move:
        board[move[0]][move[1]] = cpu_symbol

# ---------------- Rounded Button ----------------
class Button:
    def __init__(self, text, center_fn, on_click, font=button_font,
                 padx=28, pady=12, radius=16,
                 bg_rgba=(0, 0, 0, 150), hover_rgba=(255, 255, 255, 60),
                 text_color=TEXT_COLOR, outline_rgba=(255, 255, 255, 120)):
        """
        center_fn: callable -> (cx, cy) that returns the center position
                   (so buttons stay correctly placed after resizing)
        """
        self.text = text
        self.center_fn = center_fn
        self.on_click = on_click
        self.font = font
        self.padx, self.pady = padx, pady
        self.radius = radius
        self.bg_rgba = bg_rgba
        self.hover_rgba = hover_rgba
        self.text_color = text_color
        self.outline_rgba = outline_rgba
        self._recalc()

    def _recalc(self):
        self.text_surf = self.font.render(self.text, True, self.text_color)
        w = self.text_surf.get_width() + 2 * self.padx
        h = self.text_surf.get_height() + 2 * self.pady
        cx, cy = self.center_fn()
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (int(cx), int(cy))

    def draw(self, surf, mouse_pos):
        # Recompute position/size every frame in case of window resize
        self._recalc()
        is_hover = self.rect.collidepoint(mouse_pos)

        # Draw semi-transparent rounded rectangle on its own surface
        btn_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            btn_surf, self.hover_rgba if is_hover else self.bg_rgba,
            btn_surf.get_rect(), border_radius=self.radius
        )
        # Optional thin outline for definition
        pygame.draw.rect(
            btn_surf, self.outline_rgba,
            btn_surf.get_rect(), width=1, border_radius=self.radius
        )
        surf.blit(btn_surf, self.rect.topleft)

        # Draw text centered
        text_rect = self.text_surf.get_rect(center=self.rect.center)
        surf.blit(self.text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.on_click):
                    self.on_click()

# ---------------- Buttons (built per state) ----------------
start_buttons = []
symbol_buttons = []
restart_buttons = []

def build_start_buttons():
    global start_buttons
    def pvp_center(): return (WIDTH // 2, HEIGHT // 2 - 20)
    def cpu_center(): return (WIDTH // 2, HEIGHT // 2 + 60)

    start_buttons = [
        Button("Play PvP", pvp_center, on_click=lambda: start_pvp()),
        Button("Play vs Computer", cpu_center, on_click=lambda: go_symbol_select())
    ]

def build_symbol_buttons():
    global symbol_buttons
    def as_x_center(): return (WIDTH // 2, HEIGHT // 2 - 20)
    def as_o_center(): return (WIDTH // 2, HEIGHT // 2 + 60)

    symbol_buttons = [
        Button("Play as X", as_x_center, on_click=lambda: choose_symbol('X')),
        Button("Play as O", as_o_center, on_click=lambda: choose_symbol('O')),
    ]

def build_restart_buttons():
    global restart_buttons
    def again_center(): return (WIDTH // 2, HEIGHT // 2 - 20)
    def back_center():  return (WIDTH // 2, HEIGHT // 2 + 60)

    restart_buttons = [
        Button("Play Again", again_center, on_click=lambda: play_again()),
        Button("Back to Main Menu", back_center, on_click=lambda: back_to_menu()),
    ]

# ---------------- Button callbacks ----------------
def start_pvp():
    global mode, on_start_screen, on_symbol_select
    mode = "pvp"
    on_start_screen = False
    on_symbol_select = False
    restart_game()

def go_symbol_select():
    global mode, on_start_screen, on_symbol_select
    mode = "cpu"
    on_start_screen = False
    on_symbol_select = True

def choose_symbol(symbol):
    global player_symbol, cpu_symbol, player, on_symbol_select
    player_symbol = symbol
    cpu_symbol = 'O' if symbol == 'X' else 'X'
    player = 'X'  # X always starts
    on_symbol_select = False
    restart_game()
    if cpu_symbol == 'X':
        cpu_move()
        # back to human
        player = player_symbol

def play_again():
    global on_restart_screen
    restart_game()
    if mode == "cpu" and cpu_symbol == 'X':
        cpu_move()
        # back to human
        player = player_symbol
    on_restart_screen = False

def back_to_menu():
    global on_restart_screen, on_start_screen, on_symbol_select, mode
    on_restart_screen = False
    on_symbol_select = False
    on_start_screen = True
    mode = None
    restart_game()

# Build initial button sets
build_start_buttons()
build_symbol_buttons()
build_restart_buttons()

# ---------------- Main loop ----------------
running = True
while running:
    draw_background()

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = max(320, event.w), max(320, event.h)
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            update_sizes()
            # Buttons recompute their centers every frame with center_fn()

        # Toggle music
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m and pygame.mixer.get_init():
                if music_playing:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                music_playing = not music_playing

        # ---------------- Start screen ----------------
        if on_start_screen:
            for b in start_buttons:
                b.handle_event(event)

        # ---------------- Symbol select screen ----------------
        elif on_symbol_select:
            for b in symbol_buttons:
                b.handle_event(event)

        # ---------------- Game screen ----------------
        elif not game_over and not on_restart_screen:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if (BOARD_LEFT <= mx < BOARD_LEFT + BOARD_SIZE and
                        BOARD_TOP  <= my < BOARD_TOP  + BOARD_SIZE):
                    clicked_row = (my - BOARD_TOP) // SQUARE_SIZE
                    clicked_col = (mx - BOARD_LEFT) // SQUARE_SIZE

                    if board[clicked_row][clicked_col] == '':
                        if mode == "pvp":
                            board[clicked_row][clicked_col] = player
                            winner = check_winner()
                            if winner or is_full():
                                game_over, on_restart_screen = True, True
                            else:
                                player = 'O' if player == 'X' else 'X'

                        elif mode == "cpu" and player == player_symbol:
                            board[clicked_row][clicked_col] = player_symbol
                            winner = check_winner()
                            if winner or is_full():
                                game_over, on_restart_screen = True, True
                            else:
                                player = cpu_symbol
                                cpu_move()
                                winner = check_winner()
                                if winner or is_full():
                                    game_over, on_restart_screen = True, True
                                else:
                                    player = player_symbol

        # ---------------- Restart screen ----------------
        elif on_restart_screen:
            for b in restart_buttons:
                b.handle_event(event)

    # ---------------- Draw UI ----------------
    if on_start_screen:
        # Title
        title_surf = title_font.render("TIC TAC TOE", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        screen.blit(title_surf, title_rect)

        # Buttons
        for b in start_buttons:
            b.draw(screen, mouse_pos)

        # Hint
        hint = small_font.render("(Press M to mute/unmute music)", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    elif on_symbol_select:
        title_surf = title_font.render("Choose Your Symbol", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        screen.blit(title_surf, title_rect)

        for b in symbol_buttons:
            b.draw(screen, mouse_pos)

        hint = small_font.render("(Press M to mute/unmute music)", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    elif on_restart_screen:
        # Result title
        result_text = f"{winner} wins!" if winner else "It's a draw!"
        result_surf = title_font.render(result_text, True, TEXT_COLOR)
        screen.blit(result_surf, result_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

        for b in restart_buttons:
            b.draw(screen, mouse_pos)

        hint = small_font.render("(Press M to mute/unmute music)", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    else:
        # Game board & figures
        draw_lines()
        draw_figures()
        # Timer
        if timer_start:
            elapsed = int(time.time() - timer_start)
            timer_surf = font.render(f"Time: {elapsed}s", True, TEXT_COLOR)
            screen.blit(timer_surf, (10, 10))

        hint = small_font.render("(Press M to mute/unmute music)", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    pygame.display.update()

pygame.quit()
sys.exit()
    