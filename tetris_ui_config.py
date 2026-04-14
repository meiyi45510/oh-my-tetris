"""Shared UI configuration, types, and constants for the Tetris runtime."""

from dataclasses import dataclass
import os
from typing import Literal, TypeAlias

import pygame

from tetris_core import Action, BOARD_HEIGHT, BOARD_WIDTH, Color, SYSTEM6_GRAYS_4BIT

# Shared UI typing helpers.
HorizontalSpan: TypeAlias = tuple[int, int]
KeyValueRows: TypeAlias = tuple[tuple[str, str], ...]
FontKey: TypeAlias = Literal["ui", "body"]
FontMap: TypeAlias = dict[FontKey, pygame.font.Font]
TextAlign: TypeAlias = Literal["left", "center", "right"]
TextAnchor: TypeAlias = tuple[int, TextAlign]
VerticalBand: TypeAlias = tuple[int, int]
BorderStyle: TypeAlias = tuple[Color, int]
FontKeyPair: TypeAlias = tuple[FontKey, FontKey]
DEFAULT_KEY_VALUE_FONT_PAIR: FontKeyPair = ("body", "body")
STATS_FONT_PAIR: FontKeyPair = ("body", "ui")


@dataclass(frozen=True)
class SpacingScale:
    xs: int = 4
    sm: int = 6
    md: int = 8
    lg: int = 10
    xl: int = 12
    xxl: int = 16
    xxxl: int = 20


@dataclass(frozen=True)
class FontSizes:
    ui: int = 16
    body: int = 14


@dataclass(frozen=True)
class PanelLayoutConfig:
    content_inset_x: int
    content_inset_y: int


@dataclass(frozen=True)
class PreviewLayoutConfig:
    size: tuple[int, int]
    inner_padding: int
    block_margin: int
    cell_inset: int


@dataclass(frozen=True)
class ScreenConfig:
    width: int
    height: int


@dataclass(frozen=True)
class GameLayoutConfig:
    frame_width: int
    frame_height: int
    panel_width: int
    grid_size: int
    grid_width: int
    grid_height: int
    cell_inset: int
    playfield_border_width: int


@dataclass(frozen=True)
class WindowChromeConfig:
    border_width: int
    inset: int
    bar_height: int
    title_stripe_count: int
    title_stripe_spacing: int


@dataclass(frozen=True)
class TitleBarDecor:
    stripe_rows: tuple[int, ...]
    stripe_left: int
    stripe_right: int
    box_size: int
    close_box: pygame.Rect | None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHICAGO_FONT_PATH = os.path.join(BASE_DIR, "CHICAGO.TTF")
SPACING = SpacingScale()
FONT_SIZES = FontSizes()
PANEL_LAYOUT = PanelLayoutConfig(
    content_inset_x=SPACING.lg,
    content_inset_y=SPACING.lg,
)
SCREEN = ScreenConfig(width=800, height=600)
GAME_LAYOUT = GameLayoutConfig(
    frame_width=510,
    frame_height=510,
    panel_width=260,
    grid_size=25,
    grid_width=BOARD_WIDTH,
    grid_height=BOARD_HEIGHT,
    cell_inset=1,
    playfield_border_width=1,
)
WINDOW_CHROME = WindowChromeConfig(
    border_width=1,
    inset=8,
    bar_height=25,
    title_stripe_count=6,
    title_stripe_spacing=3,
)
PREVIEW_LAYOUT = PreviewLayoutConfig(
    size=(124, 74),
    inner_padding=12,
    block_margin=0,
    cell_inset=1,
)
DESKTOP_PATTERN_8X8 = (
    0x88,
    0x00,
    0x22,
    0x00,
    0x88,
    0x00,
    0x22,
    0x00,
)

UI_COLORS: dict[str, Color] = {
    "bg": SYSTEM6_GRAYS_4BIT[15],
    "desktop_pattern": SYSTEM6_GRAYS_4BIT[0],
    "playfield_bg": SYSTEM6_GRAYS_4BIT[15],
    "playfield_border": SYSTEM6_GRAYS_4BIT[0],
    "grid_line": SYSTEM6_GRAYS_4BIT[13],
    "grid_major": SYSTEM6_GRAYS_4BIT[11],
    "border": SYSTEM6_GRAYS_4BIT[0],
    "text": SYSTEM6_GRAYS_4BIT[0],
    "menu_bg": SYSTEM6_GRAYS_4BIT[15],
    "menu_text": SYSTEM6_GRAYS_4BIT[0],
    "ink": SYSTEM6_GRAYS_4BIT[0],
    "ghost": SYSTEM6_GRAYS_4BIT[7],
    "paper": SYSTEM6_GRAYS_4BIT[15],
    "title_bar_bg": SYSTEM6_GRAYS_4BIT[15],
    "title_stripe": SYSTEM6_GRAYS_4BIT[0],
    "shadow": SYSTEM6_GRAYS_4BIT[11],
}


@dataclass(frozen=True)
class ControlBinding:
    """Immutable keyboard binding metadata for input and help text."""

    action: Action
    key: int
    key_label: str
    help_text: str


MENU_ITEMS: tuple[str, ...] = ("Tetris", "File", "Edit", "View", "Special")
CONTROL_BINDINGS: tuple[ControlBinding, ...] = (
    ControlBinding(Action.MOVE_LEFT, pygame.K_a, "A", "Move Left"),
    ControlBinding(Action.MOVE_RIGHT, pygame.K_d, "D", "Move Right"),
    ControlBinding(Action.ROTATE, pygame.K_w, "W", "Rotate"),
    ControlBinding(Action.SOFT_DROP, pygame.K_s, "S", "Soft Drop"),
    ControlBinding(Action.HARD_DROP, pygame.K_SPACE, "Space", "Hard Drop"),
    ControlBinding(Action.PAUSE_RESUME, pygame.K_p, "P", "Pause / Resume"),
    ControlBinding(Action.RESTART, pygame.K_r, "R", "Restart"),
)
ACTION_BY_KEY: dict[int, Action] = {
    binding.key: binding.action
    for binding in CONTROL_BINDINGS
}
