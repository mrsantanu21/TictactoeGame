"""
Game State Manager for Tic-Tac-Toe.
Manages current board, turn, score tracking, and notifies observers.
"""

from typing import Callable, Dict, List, Optional, Tuple
from .game_logic import check_winner, check_draw, is_valid_move


class GameState:
    """
    Encapsulates game state and operations.
    Thread-safe and decoupled from the UI.
    """

    def __init__(self):
        self.board: List[str] = [""] * 9
        self.current_player: str = "X"
        self.scores: Dict[str, int] = {"X": 0, "O": 0}
        self.game_over: bool = False
        self.winning_line: Optional[Tuple[int, int, int]] = None
        self.game_mode: str = "pvp"  # "pvp" = Player vs Player, "pva" = Player vs AI (Coming Soon)
        self._listeners: List[Callable[[str, "GameState"], None]] = []

    def add_listener(self, callback: Callable[[str, "GameState"], None]) -> None:
        """Register a callback for state changes: callback(event_name, game_state)."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, "GameState"], None]) -> None:
        """Unregister a previously registered callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event: str) -> None:
        """Notify all observers of a state change event."""
        for listener in list(self._listeners):
            try:
                listener(event, self)
            except Exception as ex:
                print(f"[GameState._notify] Error notifying listener: {ex}")

    def make_move(self, position: int) -> bool:
        """
        Attempts to place the current player's mark at position (0-8).
        Returns True if the move was successful, False otherwise.
        """
        if self.game_over:
            return False
        if not is_valid_move(self.board, position):
            return False

        mark = self.current_player
        self.board[position] = mark
        self._notify("move_made")

        win = check_winner(self.board)
        if win:
            self.winning_line = win
            self.game_over = True
            self.scores[mark] += 1
            self._notify("game_won")
            return True

        if check_draw(self.board, self.winning_line):
            self.game_over = True
            self._notify("game_draw")
            return True

        self.switch_player()
        return True

    def switch_player(self) -> None:
        """Switches turn between Player X and Player O."""
        self.current_player = "O" if self.current_player == "X" else "X"
        self._notify("turn_switched")

    def reset_board(self) -> None:
        """Resets the board for a new round while preserving existing scores."""
        self.board = [""] * 9
        self.current_player = "X"
        self.game_over = False
        self.winning_line = None
        self._notify("board_reset")

    def reset_scores(self) -> None:
        """Resets scores to 0 and starts a fresh round."""
        self.scores = {"X": 0, "O": 0}
        self.reset_board()
        self._notify("scores_reset")

    def set_game_mode(self, mode: str) -> None:
        """Sets game mode ('pvp' or 'pva')."""
        if mode in ("pvp", "pva"):
            self.game_mode = mode
            self.reset_board()
            self._notify("mode_changed")
