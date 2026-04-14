"""Stateless geometry and layout helpers for the Tetris UI."""

from typing import Sequence

import pygame

from tetris_core import Position, Tetromino
from tetris_ui_config import (
    GAME_LAYOUT,
    HorizontalSpan,
    PANEL_LAYOUT,
    PREVIEW_LAYOUT,
    SCREEN,
    TitleBarDecor,
    WINDOW_CHROME,
)


def get_window_origin(window_width: int, window_height: int) -> Position:
    start_x = (SCREEN.width - window_width) // 2
    available_top = WINDOW_CHROME.bar_height + WINDOW_CHROME.inset
    available_bottom = SCREEN.height - WINDOW_CHROME.inset
    available_height = max(0, available_bottom - available_top)
    start_y = available_top + max(0, (available_height - window_height) // 2)
    return start_x, start_y


def get_window_size(frame_width: int, frame_height: int) -> tuple[int, int]:
    window_width = frame_width + 2 * WINDOW_CHROME.border_width
    window_height = (
        WINDOW_CHROME.bar_height + frame_height + 2 * WINDOW_CHROME.border_width
    )
    return window_width, window_height


def build_window_rects(
    start: Position,
    window_size: tuple[int, int],
    frame_size: tuple[int, int],
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    start_x, start_y = start
    window_width, window_height = window_size
    frame_width, frame_height = frame_size
    window_outer = pygame.Rect(start_x, start_y, window_width, window_height)
    window_title_rect = pygame.Rect(
        window_outer.x + WINDOW_CHROME.border_width,
        window_outer.y + WINDOW_CHROME.border_width,
        frame_width,
        WINDOW_CHROME.bar_height,
    )
    window_content_rect = pygame.Rect(
        window_outer.x + WINDOW_CHROME.border_width,
        window_title_rect.bottom,
        frame_width,
        frame_height,
    )
    return window_outer, window_title_rect, window_content_rect


def build_panel_rects(
    window_content_rect: pygame.Rect,
    frame_height: int,
    divider_width: int,
) -> tuple[pygame.Rect, int, pygame.Rect]:
    game_panel_rect = pygame.Rect(
        window_content_rect.x,
        window_content_rect.y,
        GAME_LAYOUT.panel_width,
        frame_height,
    )
    content_divider_x = game_panel_rect.right
    sidebar_width = GAME_LAYOUT.frame_width - GAME_LAYOUT.panel_width - divider_width
    sidebar_rect = pygame.Rect(
        content_divider_x + divider_width,
        window_content_rect.y,
        sidebar_width,
        frame_height,
    )
    return game_panel_rect, content_divider_x, sidebar_rect


def build_playfield_rect(
    playfield_size: tuple[int, int],
    game_panel_rect: pygame.Rect,
) -> pygame.Rect:
    playfield_width, playfield_height = playfield_size
    playfield_rect = pygame.Rect(0, 0, playfield_width, playfield_height)
    playfield_rect.center = game_panel_rect.center
    return playfield_rect


def build_title_bar_decor(
    title_bar_rect: pygame.Rect,
    show_close_box: bool,
) -> TitleBarDecor:
    stripe_block_height = 1 + WINDOW_CHROME.title_stripe_spacing * (
        WINDOW_CHROME.title_stripe_count - 1
    )
    stripe_block_top = title_bar_rect.y + max(
        0,
        (title_bar_rect.height - stripe_block_height) // 2,
    )
    stripe_rows = tuple(
        stripe_block_top + WINDOW_CHROME.title_stripe_spacing * index
        for index in range(WINDOW_CHROME.title_stripe_count)
    )
    box_size = stripe_rows[-1] - stripe_rows[0] + 1
    close_box = None
    if show_close_box:
        close_box = pygame.Rect(
            title_bar_rect.x + 10,
            stripe_rows[0],
            box_size,
            box_size,
        )
    return TitleBarDecor(
        stripe_rows=stripe_rows,
        stripe_left=title_bar_rect.x + 1,
        stripe_right=title_bar_rect.right - 2,
        box_size=box_size,
        close_box=close_box,
    )


def merge_horizontal_spans(
    spans: Sequence[HorizontalSpan],
    min_x: int,
    max_x: int,
) -> list[HorizontalSpan]:
    merged_spans: list[HorizontalSpan] = []
    for span_start, span_end in sorted(spans):
        clamped_start = max(min_x, span_start)
        clamped_end = min(max_x, span_end)
        if clamped_start > clamped_end:
            continue
        if not merged_spans or clamped_start > merged_spans[-1][1] + 1:
            merged_spans.append((clamped_start, clamped_end))
            continue
        previous_start, previous_end = merged_spans[-1]
        merged_spans[-1] = (previous_start, max(previous_end, clamped_end))
    return merged_spans


def get_sidebar_content_rect(rect: pygame.Rect) -> pygame.Rect:
    return rect.inflate(
        -2 * PANEL_LAYOUT.content_inset_x,
        -2 * PANEL_LAYOUT.content_inset_y,
    )


def make_inset_rect(x: int, y: int, size: int, inset: int) -> pygame.Rect:
    return pygame.Rect(
        x + inset,
        y + inset,
        size - 2 * inset,
        size - 2 * inset,
    )


def get_visible_piece_positions(piece: Tetromino) -> list[Position]:
    return [
        (x, y)
        for x, y in piece.get_positions()
        if 0 <= y < GAME_LAYOUT.grid_height
    ]


def get_preview_geometry(
    preview_rect: pygame.Rect,
    bounds: tuple[int, int, int, int],
) -> tuple[Position, int]:
    min_row, max_row, min_col, max_col = bounds
    cells_wide = max_col - min_col + 1
    cells_high = max_row - min_row + 1
    inner_rect = preview_rect.inflate(
        -2 * PREVIEW_LAYOUT.inner_padding,
        -2 * PREVIEW_LAYOUT.inner_padding,
    )
    block_size = GAME_LAYOUT.grid_size - PREVIEW_LAYOUT.block_margin
    shape_width = cells_wide * block_size
    shape_height = cells_high * block_size
    start_x = inner_rect.x + (inner_rect.width - shape_width) // 2 - min_col * block_size
    start_y = inner_rect.y + (inner_rect.height - shape_height) // 2 - min_row * block_size
    return (start_x, start_y), block_size


def get_shape_bounds(
    shape: Sequence[Sequence[int]],
) -> tuple[int, int, int, int] | None:
    if not shape:
        return None
    non_empty_rows = [i for i, row in enumerate(shape) if any(row)]
    if not non_empty_rows:
        return None
    non_empty_cols = [
        col_index
        for col_index in range(len(shape[0]))
        if any(shape[row_index][col_index] for row_index in range(len(shape)))
    ]
    if not non_empty_cols:
        return None
    min_row, max_row = min(non_empty_rows), max(non_empty_rows)
    min_col, max_col = min(non_empty_cols), max(non_empty_cols)
    return min_row, max_row, min_col, max_col


def get_desktop_rect() -> pygame.Rect:
    return pygame.Rect(
        0,
        WINDOW_CHROME.bar_height,
        SCREEN.width,
        SCREEN.height - WINDOW_CHROME.bar_height,
    )


def get_menu_bar_rect() -> pygame.Rect:
    return pygame.Rect(0, 0, SCREEN.width, WINDOW_CHROME.bar_height)
