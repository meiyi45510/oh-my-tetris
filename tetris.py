"""Pygame runtime loop and entry point for the split Tetris runtime."""

import sys

import pygame

from tetris_core import (
    Action,
    GameState,
    GameplayEngine,
    Grid,
    Position,
    Tetromino,
    TIMING,
    is_piece_action,
    is_release_action,
)
from tetris_ui import TetrisUI
from tetris_ui_config import ACTION_BY_KEY, GAME_LAYOUT, WINDOW_CHROME


class TetrisGame(TetrisUI):
    """Owns the gameplay engine, input dispatch, and main loop."""

    def __init__(self) -> None:
        super().__init__()
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.engine = GameplayEngine(
            grid_width=GAME_LAYOUT.grid_width,
            grid_height=GAME_LAYOUT.grid_height,
            timing=TIMING,
        )
        self.state = GameState.PAUSED

    @property
    def grid(self) -> Grid:
        return self.engine.grid

    @property
    def score(self) -> int:
        return self.engine.score

    @property
    def level(self) -> int:
        return self.engine.level

    @property
    def lines(self) -> int:
        return self.engine.lines

    @property
    def state(self) -> GameState:
        return self.engine.state

    @state.setter
    def state(self, next_state: GameState) -> None:
        self.engine.state = next_state

    @property
    def current_piece(self) -> Tetromino | None:
        return self.engine.current_piece

    @property
    def next_piece(self) -> Tetromino | None:
        return self.engine.next_piece

    def _reset_game(self) -> None:
        self.engine.reset_game()

    def _reset_input_state(self) -> None:
        self.engine.reset_input_state()

    def _get_shadow_piece(self) -> Tetromino:
        return self.engine.get_shadow_piece()

    def _toggle_pause(self) -> None:
        self.engine.toggle_pause()

    def _dispatch_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self.quit_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(event.pos)
        elif self.window_focused and event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif self.window_focused and event.type == pygame.KEYUP:
            self._handle_keyup(event.key)

    def _handle_mouse_click(self, pos: Position) -> None:
        if self._window_contains_point(pos):
            if not self.window_focused:
                self._activate_window()
                return
            if self.close_box_rect and self.close_box_rect.collidepoint(pos):
                self.quit_game()
        elif pos[1] >= WINDOW_CHROME.bar_height:
            self._deactivate_window()

    def _handle_keydown(self, key: int) -> None:
        action = ACTION_BY_KEY.get(key)
        if action is None:
            return
        if action == Action.RESTART:
            self._reset_game()
        elif action == Action.PAUSE_RESUME:
            self._toggle_pause()
        elif self.state == GameState.PLAYING and is_piece_action(action):
            self.engine.handle_piece_action(action)

    def _handle_keyup(self, key: int) -> None:
        action = ACTION_BY_KEY.get(key)
        if is_release_action(action):
            self.engine.handle_key_release(action)

    def _handle_input(self) -> None:
        for event in pygame.event.get():
            self._dispatch_event(event)

    def update(self, delta_ms: float) -> None:
        self.engine.update(delta_ms)

    @staticmethod
    def quit_game(exit_code: int = 0) -> None:
        pygame.quit()
        sys.exit(exit_code)

    def run(self) -> None:
        while True:
            delta_ms = self.clock.tick(60)
            self._handle_input()
            self.update(delta_ms)
            self.draw()


def main() -> None:
    try:
        game = TetrisGame()
    except RuntimeError as startup_error:
        print(startup_error, file=sys.stderr)
        TetrisGame.quit_game(1)
    else:
        game.run()


if __name__ == "__main__":
    main()
