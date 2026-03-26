import os
import random
import sys

import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
CONTROL_WIDTH = 200
BORDER_WIDTH = 4
GRID_PADDING = 6
PADDING = 8
GAP = 20

SHAPES = [
    [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
        [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
    ],
    [
        [[1, 1], [1, 1]],
        [[1, 1], [1, 1]],
        [[1, 1], [1, 1]],
        [[1, 1], [1, 1]]
    ],
    [
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 1, 0], [0, 1, 0]]
    ],
    [
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
        [[0, 0, 0], [0, 1, 1], [1, 1, 0]],
        [[1, 0, 0], [1, 1, 0], [0, 1, 0]]
    ],
    [
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 0], [0, 1, 1]],
        [[0, 1, 0], [1, 1, 0], [1, 0, 0]]
    ],
    [
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
        [[0, 1, 0], [0, 1, 0], [1, 1, 0]]
    ],
    [
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
        [[0, 0, 0], [1, 1, 1], [1, 0, 0]],
        [[1, 1, 0], [0, 1, 0], [0, 1, 0]]
    ]
]

JLSTZ_WALL_KICKS = [
    [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
    [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
    [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
    [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
    [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
    [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
    [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
    [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]]
]

I_WALL_KICKS = [
    [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
    [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
    [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
    [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
    [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
    [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
    [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
    [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]]
]

COLORS = [
    (155, 188, 155),
    (222, 222, 120),
    (155, 120, 188),
    (120, 188, 120),
    (188, 120, 120),
    (120, 155, 222),
    (222, 155, 120)
]

UI_COLORS = {
    'bg': (12, 35, 64),
    'game_bg': (24, 60, 94),
    'grid_line': (80, 110, 130),
    'sidebar_bg': (18, 45, 78),
    'control_bg': (30, 70, 100),
    'border': (140, 170, 170),
    'text': (200, 220, 210),
    'highlight': (240, 240, 160),
    'error': (220, 140, 140),
    'paused': (150, 190, 220),
    'shadow': (60, 85, 100)
}

CONTROLS = [
    ("MOVE LEFT:", "A"),
    ("MOVE RIGHT:", "D"),
    ("ROTATE:", "W"),
    ("SOFT DROP:", "S"),
    ("HARD DROP:", "SPACE"),
    ("PAUSE:", "P"),
    ("RESTART:", "R")
]

TIPS = [
    "ROTATE BLOCKS TO",
    "FIND BEST FIT",
    "",
    "CLEAR SINGLE LINES",
    "TO STAY FLAT",
    "",
    "PLAN NEXT SHAPE",
    "IN YOUR MIND"
]

SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}
FALL_FRAMES = [
    48, 43, 38, 33, 28, 23, 18, 13, 8, 6,
    5, 5, 5, 4, 4, 4, 3, 3, 3, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 1
]

GAME_PLAYING, GAME_PAUSED, GAME_OVER = range(3)


class Tetromino:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.rotation = 0
        self.shape = SHAPES[shape_idx][self.rotation]
        self.color = COLORS[shape_idx]

    def get_shape_matrix(self, rotation=None):
        if rotation is None:
            rotation = self.rotation
        return SHAPES[self.shape_idx][rotation]

    def rotate_clockwise(self):
        return (self.rotation + 1) % 4

    def get_positions(self, dx=0, dy=0, rotation=None):
        positions = []
        shape_matrix = self.get_shape_matrix(rotation) if rotation is not None else self.shape
        for y, row in enumerate(shape_matrix):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x + dx, self.y + y + dy))
        return positions

    def copy(self):
        new_piece = Tetromino(self.x, self.y, self.shape_idx)
        new_piece.rotation = self.rotation
        new_piece.shape = self.get_shape_matrix()
        return new_piece


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TETRIS")
        pygame.key.stop_text_input()
        self.clock = pygame.time.Clock()

        self.grid = []
        self.score = 0
        self.level = 0
        self.lines = 0

        self.fall_frames = 0
        self.fall_counter = 0
        self.are_counter = 0
        self.are_delay = 6

        self.das_counter = 0
        self.arr_counter = 0
        self.das_delay = 10
        self.arr_speed = 2

        self.left_held = False
        self.right_held = False
        self.move_direction = 0
        self.move_down_held = False
        self.soft_drop_counter = 0

        self.lock_delay_active = False
        self.lock_delay_counter = 0
        self.lock_delay_frames = 30

        self.bag = []
        self.current_piece = None
        self.next_piece = None
        self.state = GAME_PLAYING

        self.sidebar_outer = None
        self.game_outer = None
        self.control_outer = None
        self.sidebar_rect = None
        self.game_rect = None
        self.control_rect = None
        self.game_bg_rect = None

        self.fonts = {}

        self.setup_layout()
        self.setup_fonts()
        self.reset_game()

    def setup_layout(self):
        game_inner_width = GRID_WIDTH * GRID_SIZE
        game_inner_height = GRID_HEIGHT * GRID_SIZE
        game_width = game_inner_width + 2 * (BORDER_WIDTH + GRID_PADDING)
        game_height = game_inner_height + 2 * (BORDER_WIDTH + GRID_PADDING)

        sidebar_width = SIDEBAR_WIDTH + 2 * BORDER_WIDTH
        control_width = CONTROL_WIDTH + 2 * BORDER_WIDTH
        total_width = sidebar_width + game_width + control_width + 2 * GAP

        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = (SCREEN_HEIGHT - game_height) // 2

        self.sidebar_outer = pygame.Rect(start_x, start_y, sidebar_width, game_height)
        self.game_outer = pygame.Rect(self.sidebar_outer.right + GAP, start_y, game_width, game_height)
        self.control_outer = pygame.Rect(self.game_outer.right + GAP, start_y, control_width, game_height)

        self.sidebar_rect = pygame.Rect(
            self.sidebar_outer.x + BORDER_WIDTH,
            self.sidebar_outer.y + BORDER_WIDTH,
            SIDEBAR_WIDTH,
            game_height - 2 * BORDER_WIDTH
        )

        self.game_rect = pygame.Rect(
            self.game_outer.x + BORDER_WIDTH + GRID_PADDING,
            self.game_outer.y + BORDER_WIDTH + GRID_PADDING,
            game_inner_width,
            game_inner_height
        )

        self.control_rect = pygame.Rect(
            self.control_outer.x + BORDER_WIDTH,
            self.control_outer.y + BORDER_WIDTH,
            CONTROL_WIDTH,
            game_height - 2 * BORDER_WIDTH
        )

        self.game_bg_rect = pygame.Rect(
            self.game_outer.x + BORDER_WIDTH,
            self.game_outer.y + BORDER_WIDTH,
            game_width - 2 * BORDER_WIDTH,
            game_height - 2 * BORDER_WIDTH
        )

    def setup_fonts(self):
        font_path = "Courier.ttc"
        if not os.path.exists(font_path):
            pygame.quit()
            sys.exit()

        try:
            self.fonts = {
                'large': pygame.font.Font(font_path, 32),
                'medium': pygame.font.Font(font_path, 24),
                'small': pygame.font.Font(font_path, 18),
                'tiny': pygame.font.Font(font_path, 14)
            }
        except (OSError, RuntimeError):
            pygame.quit()
            sys.exit()

        self.fonts['large'].set_bold(True)
        self.fonts['medium'].set_bold(True)

    def reset_game(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 0
        self.lines = 0
        self.fall_frames = self.get_fall_frames()
        self.fall_counter = 0
        self.are_counter = 0
        self.das_counter = 0
        self.arr_counter = 0
        self.left_held = False
        self.right_held = False
        self.move_direction = 0
        self.move_down_held = False
        self.soft_drop_counter = 0
        self.lock_delay_active = False
        self.lock_delay_counter = 0
        self.bag = []
        self.refill_bag()
        self.current_piece = None
        self.next_piece = self.new_piece()
        self.state = GAME_PLAYING
        self.spawn_piece()

    def get_fall_frames(self):
        if self.level < len(FALL_FRAMES):
            return FALL_FRAMES[self.level]
        return FALL_FRAMES[-1]

    def refill_bag(self):
        self.bag = list(range(7))
        random.shuffle(self.bag)

    def new_piece(self):
        if not self.bag:
            self.refill_bag()
        shape_idx = self.bag.pop()
        shape_matrix = SHAPES[shape_idx][0]
        bottom_row = 0
        for y in range(len(shape_matrix) - 1, -1, -1):
            if any(shape_matrix[y]):
                bottom_row = y
                break
        x = GRID_WIDTH // 2 - len(shape_matrix[0]) // 2
        y = -bottom_row - 1
        return Tetromino(x, y, shape_idx)

    def valid_move(self, piece, dx=0, dy=0, rotation=None):
        for x, y in piece.get_positions(dx, dy, rotation):
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x]:
                return False
        return True

    def rotate_piece_srs(self):
        original_rotation = self.current_piece.rotation
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        new_rotation = self.current_piece.rotate_clockwise()
        if self.current_piece.shape_idx == 1:
            kicks = [(0, 0)]
        elif self.current_piece.shape_idx == 0:
            kicks = I_WALL_KICKS[original_rotation * 2]
        else:
            kicks = JLSTZ_WALL_KICKS[original_rotation * 2]
        for dx, dy in kicks:
            if self.valid_move(self.current_piece, dx, dy, new_rotation):
                self.current_piece.rotation = new_rotation
                self.current_piece.shape = self.current_piece.get_shape_matrix()
                self.current_piece.x += dx
                self.current_piece.y += dy
                if self.lock_delay_active:
                    self.lock_delay_active = False
                    self.lock_delay_counter = 0
                return True
        self.current_piece.rotation = original_rotation
        self.current_piece.x = original_x
        self.current_piece.y = original_y
        self.current_piece.shape = self.current_piece.get_shape_matrix()
        return False

    def lock_piece(self):
        for x, y in self.current_piece.get_positions():
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = self.current_piece.color
        if all(y < 0 for _, y in self.current_piece.get_positions()):
            self.state = GAME_OVER
            return
        self.clear_lines()
        self.current_piece = None
        self.are_counter = self.are_delay

    def clear_lines(self):
        new_grid = []
        full_lines_count = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                full_lines_count += 1
            else:
                new_grid.append(self.grid[y])
        if full_lines_count:
            for _ in range(full_lines_count):
                new_grid.insert(0, [0] * GRID_WIDTH)
            self.grid = new_grid
            self.lines += full_lines_count
            self.score += SCORES.get(full_lines_count, 0) * (self.level + 1)
            self.level = self.lines // 10
            self.fall_frames = self.get_fall_frames()

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_move(self.current_piece):
            self.state = GAME_OVER

    def get_shadow_position(self):
        shadow_piece = self.current_piece.copy()
        while self.valid_move(shadow_piece, dy=1):
            shadow_piece.y += 1
        return shadow_piece

    def handle_piece_input(self, key):
        if self.are_counter > 0:
            return
        if key == pygame.K_a:
            self.left_held = True
            self.right_held = False
            self.move_direction = -1
            self.das_counter = 0
            self.arr_counter = 0
            if self.valid_move(self.current_piece, dx=-1):
                self.current_piece.x -= 1
                if self.lock_delay_active:
                    self.lock_delay_active = False
                    self.lock_delay_counter = 0
        elif key == pygame.K_d:
            self.right_held = True
            self.left_held = False
            self.move_direction = 1
            self.das_counter = 0
            self.arr_counter = 0
            if self.valid_move(self.current_piece, dx=1):
                self.current_piece.x += 1
                if self.lock_delay_active:
                    self.lock_delay_active = False
                    self.lock_delay_counter = 0
        elif key == pygame.K_w:
            self.rotate_piece_srs()
        elif key == pygame.K_SPACE:
            while self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
            self.lock_piece()
        elif key == pygame.K_s:
            self.move_down_held = True
            if self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
                self.lock_delay_active = False
                self.lock_delay_counter = 0
                self.soft_drop_counter = 0

    def handle_key_up(self, key):
        if key == pygame.K_a:
            self.left_held = False
            if not self.right_held:
                self.move_direction = 0
                self.das_counter = 0
                self.arr_counter = 0
        elif key == pygame.K_d:
            self.right_held = False
            if not self.left_held:
                self.move_direction = 0
                self.das_counter = 0
                self.arr_counter = 0
        elif key == pygame.K_s:
            self.move_down_held = False
            self.soft_drop_counter = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_p:
                    if self.state == GAME_PLAYING:
                        self.state = GAME_PAUSED
                    elif self.state == GAME_PAUSED:
                        self.state = GAME_PLAYING
                if self.state == GAME_PLAYING:
                    self.handle_piece_input(event.key)
            elif event.type == pygame.KEYUP:
                self.handle_key_up(event.key)

    def handle_das_arr_movement(self):
        if self.are_counter > 0 or not self.current_piece:
            return
        if self.das_counter < self.das_delay:
            self.das_counter += 1
        else:
            self.arr_counter += 1
            if self.arr_counter >= self.arr_speed:
                self.arr_counter = 0
                if self.move_direction == -1 and self.valid_move(self.current_piece, dx=-1):
                    self.current_piece.x -= 1
                    if self.lock_delay_active:
                        self.lock_delay_active = False
                        self.lock_delay_counter = 0
                elif self.move_direction == 1 and self.valid_move(self.current_piece, dx=1):
                    self.current_piece.x += 1
                    if self.lock_delay_active:
                        self.lock_delay_active = False
                        self.lock_delay_counter = 0

    def handle_gravity(self):
        if self.are_counter > 0 or not self.current_piece:
            return
        self.fall_counter += 1
        if self.fall_counter >= self.fall_frames:
            self.fall_counter = 0
            if self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
                self.lock_delay_active = False
                self.lock_delay_counter = 0
            elif not self.lock_delay_active:
                self.lock_delay_active = True
                self.lock_delay_counter = 0

    def handle_soft_drop(self):
        if not self.move_down_held or self.are_counter > 0 or not self.current_piece:
            return
        self.soft_drop_counter += 1
        if self.soft_drop_counter >= 2:
            self.soft_drop_counter = 0
            if self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
                self.lock_delay_active = False
                self.lock_delay_counter = 0
            elif not self.lock_delay_active:
                self.lock_delay_active = True
                self.lock_delay_counter = 0
            else:
                self.lock_piece()

    def update(self):
        if self.state != GAME_PLAYING:
            return
        if self.are_counter > 0:
            self.are_counter -= 1
            if self.are_counter == 0:
                self.spawn_piece()
                self.fall_counter = 0
                self.lock_delay_active = False
                self.lock_delay_counter = 0
            return
        if not self.current_piece:
            return
        if self.move_direction != 0:
            self.handle_das_arr_movement()
        self.handle_gravity()
        self.handle_soft_drop()
        if self.lock_delay_active:
            self.lock_delay_counter += 1
            if self.lock_delay_counter >= self.lock_delay_frames:
                self.lock_piece()

    def draw_panel(self, rect, bg_color, border_color):
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, BORDER_WIDTH)

    def draw_block(self, x, y, color):
        rect = pygame.Rect(
            self.game_rect.x + x * GRID_SIZE + 1,
            self.game_rect.y + y * GRID_SIZE + 1,
            GRID_SIZE - 2, GRID_SIZE - 2
        )
        pygame.draw.rect(self.screen, color, rect)

    def draw_shadow(self):
        if not self.current_piece or not any(y >= 0 for _, y in self.current_piece.get_positions()):
            return
        shadow_piece = self.get_shadow_position()
        for x, y in shadow_piece.get_positions():
            if 0 <= y < GRID_HEIGHT:
                shadow_rect = pygame.Rect(
                    self.game_rect.x + x * GRID_SIZE + 1,
                    self.game_rect.y + y * GRID_SIZE + 1,
                    GRID_SIZE - 2, GRID_SIZE - 2
                )
                pygame.draw.rect(self.screen, UI_COLORS['shadow'], shadow_rect)

    def draw_current_piece(self):
        if not self.current_piece:
            return
        for x, y in self.current_piece.get_positions():
            if 0 <= y < GRID_HEIGHT:
                self.draw_block(x, y, self.current_piece.color)

    def draw_grid(self):
        for x in range(GRID_WIDTH + 1):
            sx = self.game_rect.x + x * GRID_SIZE
            pygame.draw.line(self.screen, UI_COLORS['grid_line'],
                             (sx, self.game_rect.y), (sx, self.game_rect.bottom))
        for y in range(GRID_HEIGHT + 1):
            sy = self.game_rect.y + y * GRID_SIZE
            pygame.draw.line(self.screen, UI_COLORS['grid_line'],
                             (self.game_rect.x, sy), (self.game_rect.right, sy))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.draw_block(x, y, self.grid[y][x])

    def draw_text(self, text, font_key, color, x, y, center_x=False, align='left'):
        font = self.fonts[font_key]
        surface = font.render(text, True, color)
        if center_x:
            x -= surface.get_width() // 2
        elif align == 'right':
            x -= surface.get_width()
        self.screen.blit(surface, (x, y))

    def draw_next_piece_preview(self):
        preview_rect = pygame.Rect(0, 0, 120, 100)
        preview_rect.center = (self.sidebar_rect.centerx,
                               self.sidebar_rect.y +
                               self.fonts['large'].get_linesize() +
                               self.fonts['medium'].get_linesize() + 122)
        self.draw_panel(pygame.Rect(
            preview_rect.x - BORDER_WIDTH,
            preview_rect.y - BORDER_WIDTH,
            preview_rect.width + 2 * BORDER_WIDTH,
            preview_rect.height + 2 * BORDER_WIDTH
        ), UI_COLORS['game_bg'], UI_COLORS['border'])
        if not self.next_piece:
            return
        shape = self.next_piece.get_shape_matrix(0)
        block_size = GRID_SIZE - 8
        non_empty_rows = [i for i, row in enumerate(shape) if any(row)]
        non_empty_cols = [j for j in range(len(shape[0])) if any(shape[i][j] for i in range(len(shape)))]
        if not non_empty_rows or not non_empty_cols:
            return
        min_row, max_row = min(non_empty_rows), max(non_empty_rows)
        min_col, max_col = min(non_empty_cols), max(non_empty_cols)
        bottom_align_y = preview_rect.centery + 15
        start_y = bottom_align_y - (max_row + 1) * block_size
        start_x = preview_rect.centerx - (max_col + min_col + 1) * block_size / 2
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        start_x + x * block_size + 1,
                        start_y + y * block_size + 1,
                        block_size - 2, block_size - 2
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)

    def draw_sidebar(self):
        large_font_height = self.fonts['large'].get_linesize()
        medium_font_height = self.fonts['medium'].get_linesize()
        self.draw_text("TETRIS", 'large', UI_COLORS['highlight'],
                       self.sidebar_rect.centerx, self.sidebar_rect.y + 18, True)
        pygame.draw.line(self.screen, UI_COLORS['border'],
                         (self.sidebar_rect.x + 10, self.sidebar_rect.y + large_font_height + 36),
                         (self.sidebar_rect.right - 10, self.sidebar_rect.y + large_font_height + 36), 1)
        self.draw_text("NEXT", 'medium', UI_COLORS['text'],
                       self.sidebar_rect.centerx, self.sidebar_rect.y + large_font_height + 54, True)
        self.draw_next_piece_preview()
        info = [
            ("SCORE", str(self.score)),
            ("LEVEL", str(self.level)),
            ("LINES", str(self.lines))
        ]
        for i, (label, value) in enumerate(info):
            y = (self.sidebar_rect.y + large_font_height + medium_font_height +
                 194 + i * (2 * medium_font_height + 32))
            self.draw_text(label, 'medium', UI_COLORS['text'],
                           self.sidebar_rect.centerx, y, True)
            self.draw_text(value, 'medium', UI_COLORS['highlight'],
                           self.sidebar_rect.centerx, y + medium_font_height + 14, True)

    def draw_control_panel(self):
        medium_font_height = self.fonts['medium'].get_linesize()
        small_font_height = self.fonts['small'].get_linesize()
        tiny_font_height = self.fonts['tiny'].get_linesize()
        self.draw_text("CONTROLS", 'medium', UI_COLORS['text'],
                       self.control_rect.centerx, self.control_rect.y + 18, True)
        pygame.draw.line(self.screen, UI_COLORS['border'],
                         (self.control_rect.x + 10, self.control_rect.y + medium_font_height + 28),
                         (self.control_rect.right - 10, self.control_rect.y + medium_font_height + 28), 1)
        start_y = self.control_rect.y + medium_font_height + 46
        for i, (desc, key) in enumerate(CONTROLS):
            y = start_y + i * (small_font_height + 10)
            self.draw_text(desc, 'small', UI_COLORS['text'],
                           self.control_rect.x + 15, y)
            self.draw_text(key, 'small', UI_COLORS['highlight'],
                           self.control_rect.right - 15, y, align='right')
        tips_y = self.control_rect.y + medium_font_height + 7 * small_font_height + 124
        self.draw_text("TIPS", 'medium', UI_COLORS['text'],
                       self.control_rect.centerx, tips_y, True)
        pygame.draw.line(self.screen, UI_COLORS['border'],
                         (self.control_rect.x + 10, tips_y + medium_font_height + 10),
                         (self.control_rect.right - 10, tips_y + medium_font_height + 10), 1)
        for i, tip in enumerate(TIPS):
            self.draw_text(tip, 'tiny', UI_COLORS['text'],
                           self.control_rect.centerx,
                           tips_y + medium_font_height + 28 + i * (tiny_font_height + 6),
                           True)

    def draw_status(self):
        if self.state == GAME_OVER:
            text = "GAME OVER - PRESS R TO RESTART"
            color = UI_COLORS['error']
        elif self.state == GAME_PAUSED:
            text = "PAUSED - PRESS P TO CONTINUE"
            color = UI_COLORS['paused']
        else:
            text = f"LEVEL: {self.level}   SCORE: {self.score}   LINES: {self.lines}"
            color = UI_COLORS['text']
        self.draw_text(text, 'small', color,
                       self.game_outer.centerx, self.game_outer.bottom + 10, True)

    def draw(self):
        self.screen.fill(UI_COLORS['bg'])
        self.draw_panel(self.sidebar_outer, UI_COLORS['sidebar_bg'], UI_COLORS['border'])
        self.draw_panel(self.game_outer, UI_COLORS['game_bg'], UI_COLORS['border'])
        self.draw_panel(self.control_outer, UI_COLORS['control_bg'], UI_COLORS['border'])
        pygame.draw.rect(self.screen, UI_COLORS['game_bg'], self.game_bg_rect)
        self.draw_grid()
        if self.state == GAME_PLAYING:
            self.draw_shadow()
        self.draw_current_piece()
        self.draw_sidebar()
        self.draw_control_panel()
        self.draw_status()
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(60)
            self.handle_input()
            self.update()
            self.draw()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
