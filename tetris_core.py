"""Gameplay core for the Tetris runtime."""

from dataclasses import dataclass
from enum import Enum, IntEnum
import random
from typing import Literal, TypeAlias, TypeGuard

Color: TypeAlias = tuple[int, int, int]
CellValue: TypeAlias = int | Color
Position: TypeAlias = tuple[int, int]
Grid: TypeAlias = list[list[CellValue]]
ShapeMatrix: TypeAlias = tuple[tuple[int, ...], ...]
RotationSet: TypeAlias = tuple[ShapeMatrix, ...]
KickTable: TypeAlias = tuple[Position, ...]


@dataclass(frozen=True)
class TimingConfig:
    frame_ms: float
    entry_delay_frames: int
    das_delay_frames: int
    arr_speed_frames: int
    soft_drop_repeat_frames: int
    lock_delay_frames: int


class GameState(IntEnum):
    PLAYING = 0
    PAUSED = 1
    OVER = 2


class Action(str, Enum):
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ROTATE = "rotate"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    PAUSE_RESUME = "pause_resume"
    RESTART = "restart"


PieceAction: TypeAlias = Literal[
    Action.MOVE_LEFT,
    Action.MOVE_RIGHT,
    Action.ROTATE,
    Action.SOFT_DROP,
    Action.HARD_DROP,
]
ReleaseAction: TypeAlias = Literal[
    Action.MOVE_LEFT,
    Action.MOVE_RIGHT,
    Action.SOFT_DROP,
]


def _freeze_shape_matrix(rows: list[list[int]]) -> ShapeMatrix:
    return tuple(tuple(row) for row in rows)


def _freeze_rotation_set(rotations: list[list[list[int]]]) -> RotationSet:
    return tuple(_freeze_shape_matrix(rotation) for rotation in rotations)


def _freeze_kick_table(kicks: list[list[int]]) -> KickTable:
    return tuple((dx, dy) for dx, dy in kicks)


def is_piece_action(action: Action | None) -> TypeGuard[PieceAction]:
    return action in {
        Action.MOVE_LEFT,
        Action.MOVE_RIGHT,
        Action.ROTATE,
        Action.SOFT_DROP,
        Action.HARD_DROP,
    }


def is_release_action(action: Action | None) -> TypeGuard[ReleaseAction]:
    return action in {
        Action.MOVE_LEFT,
        Action.MOVE_RIGHT,
        Action.SOFT_DROP,
    }


BOARD_WIDTH = 10
BOARD_HEIGHT = 20

TIMING = TimingConfig(
    frame_ms=1000 / 60,
    entry_delay_frames=6,
    das_delay_frames=10,
    arr_speed_frames=2,
    soft_drop_repeat_frames=2,
    lock_delay_frames=30,
)


SHAPES: tuple[RotationSet, ...] = tuple(
    _freeze_rotation_set(rotations)
    for rotations in [
        [
            [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
            [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
            [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
        ],
        [
            [[1, 1], [1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1], [1, 1]],
            [[1, 1], [1, 1]],
        ],
        [
            [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
            [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
            [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
            [[0, 1, 0], [1, 1, 0], [0, 1, 0]],
        ],
        [
            [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
            [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
            [[0, 0, 0], [0, 1, 1], [1, 1, 0]],
            [[1, 0, 0], [1, 1, 0], [0, 1, 0]],
        ],
        [
            [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
            [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
            [[0, 0, 0], [1, 1, 0], [0, 1, 1]],
            [[0, 1, 0], [1, 1, 0], [1, 0, 0]],
        ],
        [
            [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
            [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
            [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
            [[0, 1, 0], [0, 1, 0], [1, 1, 0]],
        ],
        [
            [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
            [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
            [[0, 0, 0], [1, 1, 1], [1, 0, 0]],
            [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
        ],
    ]
)

JLSTZ_WALL_KICKS: tuple[KickTable, ...] = tuple(
    _freeze_kick_table(kick_table)
    for kick_table in [
        [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
        [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
        [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
        [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
        [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
        [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
        [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
        [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
    ]
)

I_WALL_KICKS: tuple[KickTable, ...] = tuple(
    _freeze_kick_table(kick_table)
    for kick_table in [
        [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
        [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
        [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
        [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
        [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
        [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
        [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
        [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
    ]
)

SYSTEM6_GRAYS_4BIT: tuple[Color, ...] = tuple(
    (step * 17, step * 17, step * 17)
    for step in range(16)
)

COLORS: tuple[Color, ...] = (
    SYSTEM6_GRAYS_4BIT[2],
    SYSTEM6_GRAYS_4BIT[4],
    SYSTEM6_GRAYS_4BIT[6],
    SYSTEM6_GRAYS_4BIT[8],
    SYSTEM6_GRAYS_4BIT[10],
    SYSTEM6_GRAYS_4BIT[12],
    SYSTEM6_GRAYS_4BIT[13],
)

SCORES: dict[int, int] = {1: 40, 2: 100, 3: 300, 4: 1200}
FALL_FRAMES: tuple[int, ...] = (
    48,
    43,
    38,
    33,
    28,
    23,
    18,
    13,
    8,
    6,
    5,
    5,
    5,
    4,
    4,
    4,
    3,
    3,
    3,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1,
)


class Tetromino:
    """Active tetromino state and geometry helpers."""

    def __init__(self, x: int, y: int, shape_index: int) -> None:
        self.x: int = x
        self.y: int = y
        self.shape_index: int = shape_index
        self.rotation: int = 0
        self.color: Color = COLORS[shape_index]

    def get_shape_matrix(self, rotation: int | None = None) -> ShapeMatrix:
        return SHAPES[self.shape_index][
            self.rotation if rotation is None else rotation
        ]

    def rotate_clockwise(self) -> int:
        return (self.rotation + 1) % 4

    def get_positions(
        self,
        dx: int = 0,
        dy: int = 0,
        rotation: int | None = None,
    ) -> list[Position]:
        positions: list[Position] = []
        shape_matrix = self.get_shape_matrix(rotation)
        for y, row in enumerate(shape_matrix):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x + dx, self.y + y + dy))
        return positions

    def copy(self) -> "Tetromino":
        new_piece = Tetromino(self.x, self.y, self.shape_index)
        new_piece.rotation = self.rotation
        return new_piece


class GameplayEngine:
    """Owns board state, timing, and piece rules."""

    def __init__(
        self,
        grid_width: int = BOARD_WIDTH,
        grid_height: int = BOARD_HEIGHT,
        timing: TimingConfig = TIMING,
    ) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.timing = timing

        self.grid: Grid = []
        self.score: int = 0
        self.level: int = 0
        self.lines: int = 0
        self.state: GameState = GameState.PLAYING

        self.entry_delay_active: bool = False
        self.entry_delay_ms: float = self._frames_to_ms(self.timing.entry_delay_frames)
        self.entry_delay_elapsed_ms: float = 0.0
        self.das_delay_ms: float = self._frames_to_ms(self.timing.das_delay_frames)
        self.arr_interval_ms: float = self._frames_to_ms(self.timing.arr_speed_frames)
        self.soft_drop_interval_ms: float = self._frames_to_ms(
            self.timing.soft_drop_repeat_frames
        )
        self.lock_delay_ms: float = self._frames_to_ms(self.timing.lock_delay_frames)
        self.lock_delay_active: bool = False
        self.lock_delay_elapsed_ms: float = 0.0
        self.fall_interval_ms: float = 0.0
        self.gravity_elapsed_ms: float = 0.0

        self.piece_bag: list[int] = []
        self.current_piece: Tetromino | None = None
        self.next_piece: Tetromino | None = None

        self.left_held: bool = False
        self.right_held: bool = False
        self.move_direction: int = 0
        self.soft_drop_held: bool = False
        self.soft_drop_elapsed_ms: float = 0.0
        self.das_elapsed_ms: float = 0.0
        self.arr_elapsed_ms: float = 0.0

        self.reset_game()

    def _get_fall_frames(self) -> int:
        return FALL_FRAMES[min(self.level, len(FALL_FRAMES) - 1)]

    def _frames_to_ms(self, frames: int) -> float:
        return frames * self.timing.frame_ms

    def _get_fall_interval_ms(self) -> float:
        return self._frames_to_ms(self._get_fall_frames())

    def _refill_piece_bag(self) -> None:
        self.piece_bag = list(range(7))
        random.shuffle(self.piece_bag)

    def _create_piece(self) -> Tetromino:
        if not self.piece_bag:
            self._refill_piece_bag()
        shape_index = self.piece_bag.pop()
        shape_matrix = SHAPES[shape_index][0]
        bottom_row = 0
        for y in range(len(shape_matrix) - 1, -1, -1):
            if any(shape_matrix[y]):
                bottom_row = y
                break
        x = self.grid_width // 2 - len(shape_matrix[0]) // 2
        y = -bottom_row - 1
        return Tetromino(x, y, shape_index)

    def _is_valid_move(
        self,
        piece: Tetromino,
        dx: int = 0,
        dy: int = 0,
        rotation: int | None = None,
    ) -> bool:
        for x, y in piece.get_positions(dx, dy, rotation):
            if x < 0 or x >= self.grid_width or y >= self.grid_height:
                return False
            if y >= 0 and self.grid[y][x]:
                return False
        return True

    def _rotate_current_piece(self) -> bool:
        if self.current_piece is None:
            raise RuntimeError("Cannot rotate without an active piece.")
        original_rotation = self.current_piece.rotation
        new_rotation = self.current_piece.rotate_clockwise()
        if self.current_piece.shape_index == 1:
            kicks = [(0, 0)]
        elif self.current_piece.shape_index == 0:
            kicks = I_WALL_KICKS[original_rotation * 2]
        else:
            kicks = JLSTZ_WALL_KICKS[original_rotation * 2]
        for dx, dy in kicks:
            if self._is_valid_move(self.current_piece, dx, dy, new_rotation):
                self.current_piece.rotation = new_rotation
                self.current_piece.x += dx
                self.current_piece.y += dy
                self._reset_lock_delay()
                return True
        return False

    def _lock_current_piece(self) -> None:
        if self.current_piece is None:
            raise RuntimeError("Cannot lock without an active piece.")
        positions = self.current_piece.get_positions()
        topped_out = False
        for x, y in positions:
            if y < 0:
                topped_out = True
                continue
            if 0 <= y < self.grid_height:
                self.grid[y][x] = self.current_piece.color
        if topped_out:
            self.state = GameState.OVER
            return
        self._clear_completed_lines()
        self.current_piece = None
        self.entry_delay_active = True
        self.entry_delay_elapsed_ms = 0.0
        self.lock_delay_active = False
        self.lock_delay_elapsed_ms = 0.0

    def _clear_completed_lines(self) -> None:
        new_grid = [row for row in self.grid if not all(row)]
        cleared = self.grid_height - len(new_grid)
        if cleared:
            self.grid = [[0] * self.grid_width for _ in range(cleared)] + new_grid
            self.lines += cleared
            self.score += SCORES.get(cleared, 0) * (self.level + 1)
            self.level = self.lines // 10
            self.fall_interval_ms = self._get_fall_interval_ms()

    def _reset_lock_delay(self) -> None:
        self.lock_delay_active = False
        self.lock_delay_elapsed_ms = 0.0
        if self.current_piece and not self._is_valid_move(self.current_piece, dy=1):
            self._start_lock_delay()

    def _start_lock_delay(self) -> bool:
        if self.lock_delay_active:
            return False
        self.lock_delay_active = True
        self.lock_delay_elapsed_ms = 0.0
        return True

    def _move_current_piece(self, dx: int = 0, dy: int = 0) -> bool:
        if not self.current_piece or not self._is_valid_move(self.current_piece, dx, dy):
            return False
        self.current_piece.x += dx
        self.current_piece.y += dy
        self._reset_lock_delay()
        return True

    def _set_horizontal_input(self, direction: int, is_pressed: bool) -> None:
        if direction < 0:
            self.left_held = is_pressed
        else:
            self.right_held = is_pressed

        if self.left_held and self.right_held:
            self.move_direction = direction if is_pressed else -direction
        elif self.left_held:
            self.move_direction = -1
        elif self.right_held:
            self.move_direction = 1
        else:
            self.move_direction = 0

        self.das_elapsed_ms = 0.0
        self.arr_elapsed_ms = 0.0

    def _spawn_piece(self) -> None:
        self.current_piece = self.next_piece
        if self.current_piece is None:
            raise RuntimeError("Next piece was not prepared.")
        self.next_piece = self._create_piece()
        self.entry_delay_active = False
        self.entry_delay_elapsed_ms = 0.0
        self.gravity_elapsed_ms = 0.0
        if not self._is_valid_move(self.current_piece):
            self.state = GameState.OVER

    def _update_horizontal_repeat(self, delta_ms: float) -> None:
        if self.entry_delay_active or not self.current_piece:
            return
        self.das_elapsed_ms += delta_ms
        if self.das_elapsed_ms <= self.das_delay_ms:
            return
        self.arr_elapsed_ms += delta_ms
        while self.arr_elapsed_ms >= self.arr_interval_ms:
            self.arr_elapsed_ms -= self.arr_interval_ms
            if not self._move_current_piece(dx=self.move_direction):
                break

    def _update_gravity(self, delta_ms: float) -> None:
        if self.entry_delay_active or not self.current_piece:
            return
        self.gravity_elapsed_ms += delta_ms
        while self.gravity_elapsed_ms >= self.fall_interval_ms:
            self.gravity_elapsed_ms -= self.fall_interval_ms
            if self._move_current_piece(dy=1):
                continue
            self.gravity_elapsed_ms = 0.0
            self._start_lock_delay()
            break

    def _update_soft_drop(self, delta_ms: float) -> None:
        if not self.soft_drop_held or self.entry_delay_active or not self.current_piece:
            return
        self.soft_drop_elapsed_ms += delta_ms
        while self.soft_drop_elapsed_ms >= self.soft_drop_interval_ms:
            self.soft_drop_elapsed_ms -= self.soft_drop_interval_ms
            if self._move_current_piece(dy=1):
                continue
            if not self.lock_delay_active:
                self._start_lock_delay()
            self.soft_drop_elapsed_ms = 0.0
            break

    def _update_entry_delay(self, delta_ms: float) -> bool:
        if not self.entry_delay_active:
            return False
        self.entry_delay_elapsed_ms += delta_ms
        if self.entry_delay_elapsed_ms < self.entry_delay_ms:
            return True
        self._spawn_piece()
        self._reset_lock_delay()
        return True

    def _update_active_piece(self, delta_ms: float) -> None:
        if self.move_direction != 0:
            self._update_horizontal_repeat(delta_ms)
        self._update_gravity(delta_ms)
        self._update_soft_drop(delta_ms)

    def _update_lock_delay(self, delta_ms: float) -> None:
        if not self.lock_delay_active:
            return
        self.lock_delay_elapsed_ms += delta_ms
        if self.lock_delay_elapsed_ms >= self.lock_delay_ms:
            self._lock_current_piece()

    def reset_board_state(self) -> None:
        self.grid = [[0] * self.grid_width for _ in range(self.grid_height)]
        self.score = 0
        self.level = 0
        self.lines = 0

    def reset_round_timers(self) -> None:
        self.fall_interval_ms = self._get_fall_interval_ms()
        self.gravity_elapsed_ms = 0.0
        self.entry_delay_active = False
        self.entry_delay_elapsed_ms = 0.0
        self.lock_delay_active = False
        self.lock_delay_elapsed_ms = 0.0

    def reset_input_state(self) -> None:
        self.left_held = False
        self.right_held = False
        self.move_direction = 0
        self.soft_drop_held = False
        self.soft_drop_elapsed_ms = 0.0
        self.das_elapsed_ms = 0.0
        self.arr_elapsed_ms = 0.0

    def reset_piece_queue(self) -> None:
        self._refill_piece_bag()
        self.current_piece = None
        self.next_piece = self._create_piece()

    def reset_game(self) -> None:
        self.reset_board_state()
        self.reset_round_timers()
        self.reset_input_state()
        self.reset_piece_queue()
        self.state = GameState.PLAYING
        self._spawn_piece()

    def get_shadow_piece(self) -> Tetromino:
        if self.current_piece is None:
            raise RuntimeError("Cannot compute shadow piece without an active piece.")
        shadow_piece = self.current_piece.copy()
        while self._is_valid_move(shadow_piece, dy=1):
            shadow_piece.y += 1
        return shadow_piece

    def handle_piece_action(self, action: PieceAction) -> None:
        if self.entry_delay_active:
            return
        if action == Action.MOVE_LEFT:
            self._set_horizontal_input(-1, True)
            self._move_current_piece(dx=-1)
        elif action == Action.MOVE_RIGHT:
            self._set_horizontal_input(1, True)
            self._move_current_piece(dx=1)
        elif action == Action.ROTATE:
            self._rotate_current_piece()
        elif action == Action.HARD_DROP:
            while self._move_current_piece(dy=1):
                pass
            self._lock_current_piece()
        elif action == Action.SOFT_DROP:
            self.soft_drop_held = True
            if self._move_current_piece(dy=1):
                self.soft_drop_elapsed_ms = 0.0

    def handle_key_release(self, action: ReleaseAction) -> None:
        if action == Action.MOVE_LEFT:
            self._set_horizontal_input(-1, False)
        elif action == Action.MOVE_RIGHT:
            self._set_horizontal_input(1, False)
        elif action == Action.SOFT_DROP:
            self.soft_drop_held = False
            self.soft_drop_elapsed_ms = 0.0

    def toggle_pause(self) -> None:
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def update(self, delta_ms: float) -> None:
        if self.state != GameState.PLAYING:
            return
        if self._update_entry_delay(delta_ms):
            return
        if not self.current_piece:
            return
        self._update_active_piece(delta_ms)
        self._update_lock_delay(delta_ms)
