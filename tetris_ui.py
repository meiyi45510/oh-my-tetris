"""Pygame UI shell, layout, and rendering helpers for the Tetris runtime."""

import os
from typing import Sequence

import pygame

from tetris_core import Color, GameState, Grid, Position, Tetromino
from tetris_ui_config import (
    BorderStyle,
    CHICAGO_FONT_PATH,
    CONTROL_BINDINGS,
    DEFAULT_KEY_VALUE_FONT_PAIR,
    DESKTOP_PATTERN_8X8,
    FONT_SIZES,
    FontKey,
    FontKeyPair,
    FontMap,
    GAME_LAYOUT,
    HorizontalSpan,
    KeyValueRows,
    MENU_ITEMS,
    PREVIEW_LAYOUT,
    SCREEN,
    SPACING,
    STATS_FONT_PAIR,
    TextAnchor,
    TitleBarDecor,
    UI_COLORS,
    VerticalBand,
    WINDOW_CHROME,
)
from tetris_ui_helpers import (
    build_panel_rects,
    build_playfield_rect,
    build_title_bar_decor,
    build_window_rects,
    get_desktop_rect,
    get_menu_bar_rect,
    get_preview_geometry,
    get_shape_bounds,
    get_sidebar_content_rect,
    get_visible_piece_positions,
    get_window_origin,
    get_window_size,
    make_inset_rect,
    merge_horizontal_spans,
)


class TetrisUI:
    """Shared Pygame window shell, layout state, and rendering helpers."""

    # Hooks implemented by the gameplay host.
    @property
    def grid(self) -> Grid:
        raise NotImplementedError

    @property
    def score(self) -> int:
        raise NotImplementedError

    @property
    def level(self) -> int:
        raise NotImplementedError

    @property
    def lines(self) -> int:
        raise NotImplementedError

    @property
    def state(self) -> GameState:
        raise NotImplementedError

    @state.setter
    def state(self, next_state: GameState) -> None:
        raise NotImplementedError

    @property
    def current_piece(self) -> Tetromino | None:
        raise NotImplementedError

    @property
    def next_piece(self) -> Tetromino | None:
        raise NotImplementedError

    def _reset_input_state(self) -> None:
        raise NotImplementedError

    def _get_shadow_piece(self) -> Tetromino:
        raise NotImplementedError

    # Lifecycle and setup.
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN.width, SCREEN.height)
        )
        pygame.display.set_caption("Tetris")
        pygame.key.stop_text_input()

        self.window_outer: pygame.Rect | None = None
        self.window_title_rect: pygame.Rect | None = None
        self.window_content_rect: pygame.Rect | None = None
        self.sidebar_rect: pygame.Rect | None = None
        self.playfield_rect: pygame.Rect | None = None
        self.close_box_rect: pygame.Rect | None = None
        self.content_divider_x: int | None = None
        self.window_focused: bool = True

        self.fonts: FontMap = {}
        self.desktop_surface: pygame.Surface | None = None
        self.menu_bar_surface: pygame.Surface | None = None

        self._setup_layout()
        self._setup_fonts()

    # Layout construction.
    _get_window_origin = staticmethod(get_window_origin)
    _get_window_size = staticmethod(get_window_size)
    _build_window_rects = staticmethod(build_window_rects)
    _build_panel_rects = staticmethod(build_panel_rects)
    _build_playfield_rect = staticmethod(build_playfield_rect)

    def _setup_layout(self) -> None:
        divider_width = 1
        frame_size = (GAME_LAYOUT.frame_width, GAME_LAYOUT.frame_height)
        playfield_size = (
            GAME_LAYOUT.grid_width * GAME_LAYOUT.grid_size,
            GAME_LAYOUT.grid_height * GAME_LAYOUT.grid_size,
        )
        window_size = self._get_window_size(*frame_size)
        start = self._get_window_origin(*window_size)
        window_outer, window_title_rect, window_content_rect = self._build_window_rects(
            start,
            window_size,
            frame_size,
        )
        game_panel_rect, content_divider_x, sidebar_rect = self._build_panel_rects(
            window_content_rect,
            frame_size[1],
            divider_width,
        )
        playfield_rect = self._build_playfield_rect(playfield_size, game_panel_rect)
        self.window_outer = window_outer
        self.window_title_rect = window_title_rect
        self.window_content_rect = window_content_rect
        self.sidebar_rect = sidebar_rect
        self.playfield_rect = playfield_rect
        self.content_divider_x = content_divider_x
        self._invalidate_static_surfaces()

    def _setup_fonts(self) -> None:
        font_path = self._get_font_path()

        try:
            self.fonts = {
                "ui": pygame.font.Font(font_path, FONT_SIZES.ui),
                "body": pygame.font.Font(font_path, FONT_SIZES.body),
            }
        except (OSError, RuntimeError) as font_error:
            raise RuntimeError(
                f"Unable to load font at {font_path}. "
                "Place CHICAGO.TTF in the project root or update CHICAGO_FONT_PATH."
            ) from font_error

    @staticmethod
    def _get_font_path() -> str:
        if os.path.exists(CHICAGO_FONT_PATH):
            return CHICAGO_FONT_PATH
        raise RuntimeError(
            f"Required font not found at {CHICAGO_FONT_PATH}. "
            "Place CHICAGO.TTF in the project root or update CHICAGO_FONT_PATH."
        )

    # Focus and window state.
    def _deactivate_window(self) -> None:
        if not self.window_focused:
            return
        self.window_focused = False
        self.close_box_rect = None
        self._reset_input_state()
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED

    def _activate_window(self) -> None:
        self.window_focused = True

    def _window_contains_point(self, pos: Position) -> bool:
        return bool(self.window_outer and self.window_outer.collidepoint(pos))

    # Primitive drawing helpers.
    def _draw_framed_rect(
        self,
        rect: pygame.Rect,
        fill_color: Color,
        border: BorderStyle,
        target_surface: pygame.Surface | None = None,
    ) -> None:
        target = self.screen if target_surface is None else target_surface
        border_color, border_width = border
        pygame.draw.rect(target, fill_color, rect)
        pygame.draw.rect(target, border_color, rect, border_width)

    def _draw_rect_outline(
        self,
        rect: pygame.Rect,
        color: Color,
        border_width: int = 1,
        target_surface: pygame.Surface | None = None,
    ) -> None:
        target = self.screen if target_surface is None else target_surface
        pygame.draw.rect(target, color, rect, border_width)

    def _draw_line(
        self,
        start: Position,
        end: Position,
        color: Color,
        target_surface: pygame.Surface | None = None,
    ) -> None:
        target = self.screen if target_surface is None else target_surface
        pygame.draw.line(target, color, start, end, 1)

    def _draw_rect_cross(self, rect: pygame.Rect, color: Color, inset: int) -> None:
        self._draw_line(
            (rect.x + inset, rect.y + inset),
            (rect.right - inset - 1, rect.bottom - inset - 1),
            color,
        )
        self._draw_line(
            (rect.right - inset - 1, rect.y + inset),
            (rect.x + inset, rect.bottom - inset - 1),
            color,
        )

    def _draw_offset_shadow(
        self,
        rect: pygame.Rect,
        dx: int = 2,
        dy: int = 2,
    ) -> None:
        pygame.draw.rect(self.screen, UI_COLORS["shadow"], rect.move(dx, dy))

    # Window chrome helpers.
    def _draw_window_shell(
        self,
        outer_rect: pygame.Rect,
        title_bar_rect: pygame.Rect,
    ) -> None:
        self._draw_offset_shadow(outer_rect, dx=2, dy=2)
        self._draw_framed_rect(
            outer_rect,
            UI_COLORS["paper"],
            (UI_COLORS["border"], WINDOW_CHROME.border_width),
        )
        pygame.draw.rect(self.screen, UI_COLORS["title_bar_bg"], title_bar_rect)
        self._draw_line(
            (title_bar_rect.x, title_bar_rect.bottom - 1),
            (title_bar_rect.right - 1, title_bar_rect.bottom - 1),
            UI_COLORS["border"],
        )

    def _draw_title_label(self, title_bar_rect: pygame.Rect, title: str) -> pygame.Rect:
        title_surface = self._render_text_surface(
            title,
            "ui",
            UI_COLORS["text"],
            tracking=0,
        )
        title_text_rect = self._blit_surface_in_band(
            title_surface,
            (title_bar_rect.centerx, "center"),
            (title_bar_rect.y, title_bar_rect.height - 1),
        )
        return title_text_rect.inflate(6, 2)

    _build_title_bar_decor = staticmethod(build_title_bar_decor)
    _merge_horizontal_spans = staticmethod(merge_horizontal_spans)

    def _draw_title_stripes(
        self,
        decor: TitleBarDecor,
        blocked_spans: Sequence[HorizontalSpan],
    ) -> None:
        for y in decor.stripe_rows:
            segment_start = decor.stripe_left
            for block_start, block_end in blocked_spans:
                if block_start > segment_start:
                    self._draw_line(
                        (segment_start, y),
                        (block_start - 1, y),
                        UI_COLORS["title_stripe"],
                    )
                segment_start = max(segment_start, block_end + 1)
            if segment_start <= decor.stripe_right:
                self._draw_line(
                    (segment_start, y),
                    (decor.stripe_right, y),
                    UI_COLORS["title_stripe"],
                )

    def _draw_close_box(self, close_box: pygame.Rect, box_size: int) -> None:
        self._draw_framed_rect(
            close_box,
            UI_COLORS["paper"],
            (UI_COLORS["border"], 1),
        )
        if not close_box.collidepoint(pygame.mouse.get_pos()):
            return
        close_inset = max(2, box_size // 4)
        self._draw_rect_cross(
            close_box,
            UI_COLORS["ink"],
            close_inset,
        )

    def _draw_window_frame(
        self,
        outer_rect: pygame.Rect,
        title_bar_rect: pygame.Rect,
        title: str,
        show_close_box: bool = True,
    ) -> pygame.Rect | None:
        self._draw_window_shell(outer_rect, title_bar_rect)
        title_bg = self._draw_title_label(title_bar_rect, title)
        decor = self._build_title_bar_decor(title_bar_rect, show_close_box)

        if self.window_focused:
            blocked_spans: list[HorizontalSpan] = [
                (title_bg.x - 3, title_bg.right + 3)
            ]
            if decor.close_box:
                blocked_spans.insert(
                    0,
                    (decor.close_box.x - 1, decor.close_box.right + 1),
                )
            merged_spans = self._merge_horizontal_spans(
                blocked_spans,
                decor.stripe_left,
                decor.stripe_right,
            )
            self._draw_title_stripes(decor, merged_spans)
            if decor.close_box:
                self._draw_close_box(decor.close_box, decor.box_size)
        return decor.close_box if show_close_box and self.window_focused else None

    def _draw_window_chrome(self) -> None:
        self.close_box_rect = self._draw_window_frame(
            self.window_outer,
            self.window_title_rect,
            "Tetris",
            show_close_box=True,
        )

    _get_sidebar_content_rect = staticmethod(get_sidebar_content_rect)

    def _draw_content_divider(self) -> None:
        if not self.window_content_rect or self.content_divider_x is None:
            return
        self._draw_line(
            (self.content_divider_x, self.window_content_rect.y),
            (self.content_divider_x, self.window_content_rect.bottom - 1),
            UI_COLORS["border"],
        )

    # Playfield rendering.
    _make_inset_rect = staticmethod(make_inset_rect)

    def _make_playfield_cell_rect(self, x: int, y: int) -> pygame.Rect:
        return self._make_inset_rect(
            self.playfield_rect.x + x * GAME_LAYOUT.grid_size,
            self.playfield_rect.y + y * GAME_LAYOUT.grid_size,
            GAME_LAYOUT.grid_size,
            GAME_LAYOUT.cell_inset,
        )

    _get_visible_piece_positions = staticmethod(get_visible_piece_positions)

    def _draw_tile_rect(self, rect: pygame.Rect, color: Color) -> None:
        self._draw_framed_rect(rect, color, (UI_COLORS["ink"], 1))

    def _draw_block(self, x: int, y: int, color: Color) -> None:
        self._draw_tile_rect(self._make_playfield_cell_rect(x, y), color)

    def _draw_shadow(self) -> None:
        if not self.current_piece:
            return
        if not self._get_visible_piece_positions(self.current_piece):
            return
        for x, y in self._get_visible_piece_positions(self._get_shadow_piece()):
            self._draw_rect_outline(
                self._make_playfield_cell_rect(x, y),
                UI_COLORS["ghost"],
            )

    def _draw_current_piece(self) -> None:
        if not self.current_piece:
            return
        for x, y in self._get_visible_piece_positions(self.current_piece):
            self._draw_block(x, y, self.current_piece.color)

    def _draw_grid(self) -> None:
        pygame.draw.rect(self.screen, UI_COLORS["playfield_bg"], self.playfield_rect)
        for x in range(1, GAME_LAYOUT.grid_width):
            grid_line_x = self.playfield_rect.x + x * GAME_LAYOUT.grid_size
            line_color = (
                UI_COLORS["grid_major"]
                if x % 5 == 0
                else UI_COLORS["grid_line"]
            )
            self._draw_line(
                (grid_line_x, self.playfield_rect.y),
                (grid_line_x, self.playfield_rect.bottom - 1),
                line_color,
            )
        for y in range(1, GAME_LAYOUT.grid_height):
            grid_line_y = self.playfield_rect.y + y * GAME_LAYOUT.grid_size
            line_color = (
                UI_COLORS["grid_major"]
                if y % 5 == 0
                else UI_COLORS["grid_line"]
            )
            self._draw_line(
                (self.playfield_rect.x, grid_line_y),
                (self.playfield_rect.right - 1, grid_line_y),
                line_color,
            )
        for y in range(GAME_LAYOUT.grid_height):
            for x in range(GAME_LAYOUT.grid_width):
                if self.grid[y][x]:
                    self._draw_block(x, y, self.grid[y][x])
        playfield_frame = self.playfield_rect.inflate(
            2 * GAME_LAYOUT.playfield_border_width,
            2 * GAME_LAYOUT.playfield_border_width,
        )
        self._draw_rect_outline(
            playfield_frame,
            UI_COLORS["playfield_border"],
            GAME_LAYOUT.playfield_border_width,
        )

    def _render_text_surface(
        self,
        text: str,
        font_key: FontKey,
        color: Color,
        tracking: int = 0,
    ) -> pygame.Surface:
        font = self.fonts[font_key]
        if tracking <= 0 or len(text) <= 1:
            return font.render(text, True, color)

        glyphs = [font.render(ch, True, color) for ch in text]
        width = (
            sum(glyph.get_width() for glyph in glyphs)
            + tracking * (len(glyphs) - 1)
        )
        height = max(
            (glyph.get_height() for glyph in glyphs),
            default=font.get_linesize(),
        )
        surface = pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)

        cursor_x = 0
        for glyph in glyphs:
            surface.blit(glyph, (cursor_x, 0))
            cursor_x += glyph.get_width() + tracking
        return surface

    def _blit_surface_in_band(
        self,
        surface: pygame.Surface,
        anchor: TextAnchor,
        band: VerticalBand,
        target_surface: pygame.Surface | None = None,
    ) -> pygame.Rect:
        x, align = anchor
        top, height = band
        target = self.screen if target_surface is None else target_surface
        rect = surface.get_rect()
        if align == "center":
            rect.centerx = x
        elif align == "right":
            rect.right = x
        else:
            rect.x = x
        rect.y = top + max(0, (height - surface.get_height()) // 2)
        target.blit(surface, rect)
        return rect

    # Sidebar text and status.
    def _draw_info_rule(self, y: int) -> int:
        if not self.sidebar_rect:
            return y + SPACING.md
        self._draw_line(
            (self.sidebar_rect.x, y),
            (self.sidebar_rect.right - 1, y),
            UI_COLORS["border"],
        )
        return y + SPACING.md

    def _get_status_line_text(self) -> str:
        if self.state == GameState.PAUSED:
            return "Paused."
        if self.state == GameState.OVER:
            return "Game Over."
        return "Ready."

    @staticmethod
    def _get_control_rows() -> KeyValueRows:
        return tuple(
            (binding.help_text, binding.key_label)
            for binding in CONTROL_BINDINGS
        )

    def _get_stats_rows(self) -> KeyValueRows:
        return (
            ("Score", f"{self.score:06d}"),
            ("Lines", f"{self.lines:03d}"),
            ("Level", f"{self.level:03d}"),
        )

    def _draw_key_value_rows(
        self,
        content_rect: pygame.Rect,
        y: int,
        rows: KeyValueRows,
        font_pair: FontKeyPair = DEFAULT_KEY_VALUE_FONT_PAIR,
    ) -> int:
        if not rows:
            return y
        label_font_key, value_font_key = font_pair

        label_surfaces = [
            self._render_text_surface(label, label_font_key, UI_COLORS["text"])
            for label, _ in rows
        ]
        value_surfaces = [
            self._render_text_surface(value, value_font_key, UI_COLORS["text"])
            for _, value in rows
        ]
        row_height = max(
            max((surface.get_height() for surface in label_surfaces), default=0),
            max((surface.get_height() for surface in value_surfaces), default=0),
        )

        for label_surface, value_surface in zip(label_surfaces, value_surfaces):
            self._blit_surface_in_band(
                label_surface,
                (content_rect.x, "left"),
                (y, row_height),
            )
            self._blit_surface_in_band(
                value_surface,
                (content_rect.right, "right"),
                (y, row_height),
            )
            y += row_height + SPACING.xs
        return y

    def _draw_next_piece_section(self, content_rect: pygame.Rect, top_y: int) -> int:
        next_label = self._render_text_surface("Next:", "body", UI_COLORS["text"])
        next_label_rect = self._blit_surface_in_band(
            next_label,
            (content_rect.x, "left"),
            (top_y, next_label.get_height()),
        )
        preview_rect = pygame.Rect(
            content_rect.x + max(
                0,
                (content_rect.width - PREVIEW_LAYOUT.size[0]) // 2,
            ),
            next_label_rect.bottom + SPACING.xs,
            PREVIEW_LAYOUT.size[0],
            PREVIEW_LAYOUT.size[1],
        )
        self._draw_next_piece_preview(preview_rect, show_frame=True)
        return preview_rect.bottom

    def _draw_stats_section(self, content_rect: pygame.Rect, top_y: int) -> int:
        rule_y = top_y + SPACING.lg
        self._draw_info_rule(rule_y)
        rows_y = rule_y + SPACING.lg
        return self._draw_key_value_rows(
            content_rect,
            rows_y,
            self._get_stats_rows(),
            font_pair=STATS_FONT_PAIR,
        )

    def _draw_controls_section(self, content_rect: pygame.Rect, top_y: int) -> int:
        rule_y = top_y + SPACING.sm
        self._draw_info_rule(rule_y)
        label_y = rule_y + SPACING.lg
        keys_label = self._render_text_surface("Keys:", "body", UI_COLORS["text"])
        keys_label_rect = self._blit_surface_in_band(
            keys_label,
            (content_rect.x, "left"),
            (label_y, keys_label.get_height()),
        )
        rows_y = keys_label_rect.bottom + SPACING.xs
        return self._draw_key_value_rows(
            content_rect,
            rows_y,
            self._get_control_rows(),
        )

    def _draw_status_section(self, content_rect: pygame.Rect) -> None:
        status_text = self._render_text_surface(
            self._get_status_line_text(),
            "body",
            UI_COLORS["text"],
        )
        status_rule_y = self.sidebar_rect.bottom - WINDOW_CHROME.bar_height
        status_band_top = status_rule_y + 1
        status_band_height = WINDOW_CHROME.bar_height - 1
        self._draw_info_rule(status_rule_y)
        self._blit_surface_in_band(
            status_text,
            (content_rect.x, "left"),
            (status_band_top, status_band_height),
        )

    def _draw_next_piece_preview(
        self,
        preview_rect: pygame.Rect,
        show_frame: bool = True,
    ) -> pygame.Rect:
        if show_frame:
            self._draw_framed_rect(
                preview_rect,
                UI_COLORS["paper"],
                (UI_COLORS["border"], 1),
            )
        next_piece = self.next_piece
        if not next_piece:
            return preview_rect

        shape = next_piece.get_shape_matrix(0)
        bounds = self._get_shape_bounds(shape)
        if bounds is None:
            return preview_rect
        start, block_size = self._get_preview_geometry(preview_rect, bounds)
        self._draw_shape_preview(shape, start, block_size, next_piece.color)

        return preview_rect

    # Next-piece preview helpers.
    _get_preview_geometry = staticmethod(get_preview_geometry)

    def _draw_shape_preview(
        self,
        shape: Sequence[Sequence[int]],
        start: Position,
        block_size: int,
        color: Color,
    ) -> None:
        start_x, start_y = start
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if not cell:
                    continue
                rect = self._make_inset_rect(
                    start_x + x * block_size,
                    start_y + y * block_size,
                    block_size,
                    PREVIEW_LAYOUT.cell_inset,
                )
                self._draw_tile_rect(rect, color)

    _get_shape_bounds = staticmethod(get_shape_bounds)

    def _draw_sidebar(self) -> None:
        content_rect = self._get_sidebar_content_rect(self.sidebar_rect)
        section_bottom = self._draw_next_piece_section(content_rect, content_rect.y)
        section_bottom = self._draw_stats_section(content_rect, section_bottom)
        self._draw_controls_section(content_rect, section_bottom)
        self._draw_status_section(content_rect)

    # Cached surfaces and frame composition.
    _get_desktop_rect = staticmethod(get_desktop_rect)
    _get_menu_bar_rect = staticmethod(get_menu_bar_rect)

    def _build_desktop_surface(self) -> pygame.Surface:
        desktop_rect = self._get_desktop_rect()
        surface = pygame.Surface(desktop_rect.size)
        surface.fill(UI_COLORS["bg"])
        for local_y in range(desktop_rect.height):
            global_y = desktop_rect.y + local_y
            pattern_row = DESKTOP_PATTERN_8X8[global_y % len(DESKTOP_PATTERN_8X8)]
            for local_x in range(desktop_rect.width):
                global_x = desktop_rect.x + local_x
                bit_index = 7 - (global_x % 8)
                if pattern_row & (1 << bit_index):
                    surface.set_at((local_x, local_y), UI_COLORS["desktop_pattern"])
        return surface

    def _build_menu_bar_surface(self) -> pygame.Surface:
        menu_rect = self._get_menu_bar_rect()
        surface = pygame.Surface(menu_rect.size)
        pygame.draw.rect(surface, UI_COLORS["menu_bg"], surface.get_rect())
        self._draw_line(
            (0, menu_rect.height - 1),
            (menu_rect.width - 1, menu_rect.height - 1),
            UI_COLORS["border"],
            target_surface=surface,
        )
        x = 10
        menu_content_height = menu_rect.height - 1
        menu_gap = max(14, self.fonts["ui"].size("  ")[0] + 8)
        for item in MENU_ITEMS:
            item_surface = self._render_text_surface(
                item,
                "ui",
                UI_COLORS["menu_text"],
                tracking=1,
            )
            item_rect = self._blit_surface_in_band(
                item_surface,
                (x, "left"),
                (0, menu_content_height),
                target_surface=surface,
            )
            x = item_rect.right + menu_gap
        return surface

    def _invalidate_static_surfaces(self) -> None:
        self.desktop_surface = None
        self.menu_bar_surface = None

    def _ensure_static_surfaces(self) -> None:
        if self.desktop_surface is None:
            self.desktop_surface = self._build_desktop_surface()
        if self.menu_bar_surface is None:
            self.menu_bar_surface = self._build_menu_bar_surface()

    def _draw_desktop(self) -> None:
        self._ensure_static_surfaces()
        self.screen.blit(self.desktop_surface, self._get_desktop_rect().topleft)

    def _draw_menu_bar(self) -> None:
        self._ensure_static_surfaces()
        self.screen.blit(self.menu_bar_surface, self._get_menu_bar_rect().topleft)

    def _draw_playfield_layer(self) -> None:
        self._draw_grid()
        if self.state == GameState.PLAYING:
            self._draw_shadow()
        self._draw_current_piece()

    def _draw_window_contents(self) -> None:
        self._draw_content_divider()
        self._draw_playfield_layer()
        self._draw_sidebar()

    def draw(self) -> None:
        self._draw_desktop()
        self._draw_menu_bar()
        self._draw_window_chrome()
        self._draw_window_contents()
        pygame.display.flip()
