"""
Unit tests for Tic-Tac-Toe Game Logic and Game State.
Runs completely independent of Kivy or UI.
"""

import sys
import os
# Ensure the project root is on the path so 'game' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from game.game_logic import (
    WINNING_COMBINATIONS,
    check_winner,
    check_draw,
    is_valid_move,
    get_available_moves,
)
from game.game_state import GameState


class TestGameLogic(unittest.TestCase):

    def test_winning_combinations_count(self):
        """Must have exactly 8 winning combinations (3 horizontal, 3 vertical, 2 diagonal)."""
        self.assertEqual(len(WINNING_COMBINATIONS), 8)

    def test_horizontal_wins(self):
        """Test all three horizontal rows."""
        # Row 0: 0, 1, 2
        board = ["X", "X", "X", "", "", "", "", "", ""]
        self.assertEqual(check_winner(board), (0, 1, 2))

        # Row 1: 3, 4, 5
        board = ["", "", "", "O", "O", "O", "", "", ""]
        self.assertEqual(check_winner(board), (3, 4, 5))

        # Row 2: 6, 7, 8
        board = ["", "", "", "", "", "", "X", "X", "X"]
        self.assertEqual(check_winner(board), (6, 7, 8))

    def test_vertical_wins(self):
        """Test all three vertical columns."""
        # Col 0: 0, 3, 6
        board = ["O", "", "", "O", "", "", "O", "", ""]
        self.assertEqual(check_winner(board), (0, 3, 6))

        # Col 1: 1, 4, 7
        board = ["", "X", "", "", "X", "", "", "X", ""]
        self.assertEqual(check_winner(board), (1, 4, 7))

        # Col 2: 2, 5, 8
        board = ["", "", "O", "", "", "O", "", "", "O"]
        self.assertEqual(check_winner(board), (2, 5, 8))

    def test_diagonal_wins(self):
        """Test both diagonals."""
        # Main diagonal: 0, 4, 8
        board = ["X", "", "", "", "X", "", "", "", "X"]
        self.assertEqual(check_winner(board), (0, 4, 8))

        # Anti diagonal: 2, 4, 6
        board = ["", "", "O", "", "O", "", "O", "", ""]
        self.assertEqual(check_winner(board), (2, 4, 6))

    def test_no_false_winners(self):
        """Empty board or mixed board with no three-in-a-row."""
        empty_board = [""] * 9
        self.assertIsNone(check_winner(empty_board))

        mixed_board = ["X", "O", "X", "X", "O", "O", "O", "X", ""]
        self.assertIsNone(check_winner(mixed_board))

    def test_draw_detection(self):
        """Full board with no winner should be a draw."""
        draw_board = [
            "X", "O", "X",
            "X", "O", "O",
            "O", "X", "X"
        ]
        self.assertIsNone(check_winner(draw_board))
        self.assertTrue(check_draw(draw_board))

        # Not a draw if winning line exists
        win_board = [
            "X", "X", "X",
            "O", "O", "X",
            "O", "X", "O"
        ]
        self.assertFalse(check_draw(win_board, winning_line=(0, 1, 2)))

    def test_valid_moves(self):
        board = ["X", "", "", "", "O", "", "", "", ""]
        self.assertFalse(is_valid_move(board, 0))
        self.assertTrue(is_valid_move(board, 1))
        self.assertFalse(is_valid_move(board, 4))
        self.assertFalse(is_valid_move(board, -1))
        self.assertFalse(is_valid_move(board, 9))
        self.assertEqual(get_available_moves(board), [1, 2, 3, 5, 6, 7, 8])


class TestGameState(unittest.TestCase):

    def setUp(self):
        self.state = GameState()

    def test_initial_state(self):
        self.assertEqual(self.state.board, [""] * 9)
        self.assertEqual(self.state.current_player, "X")
        self.assertEqual(self.state.scores, {"X": 0, "O": 0})
        self.assertFalse(self.state.game_over)
        self.assertIsNone(self.state.winning_line)

    def test_turn_switching(self):
        self.state.make_move(0)  # X plays 0
        self.assertEqual(self.state.board[0], "X")
        self.assertEqual(self.state.current_player, "O")

        self.state.make_move(1)  # O plays 1
        self.assertEqual(self.state.board[1], "O")
        self.assertEqual(self.state.current_player, "X")

    def test_cannot_play_occupied_cell(self):
        self.state.make_move(0)
        result = self.state.make_move(0)
        self.assertFalse(result)
        self.assertEqual(self.state.current_player, "O")  # Still O's turn

    def test_win_updates_score_and_game_over(self):
        # X: 0, 1, 2
        # O: 3, 4
        self.state.make_move(0)  # X
        self.state.make_move(3)  # O
        self.state.make_move(1)  # X
        self.state.make_move(4)  # O
        self.state.make_move(2)  # X wins!

        self.assertTrue(self.state.game_over)
        self.assertEqual(self.state.winning_line, (0, 1, 2))
        self.assertEqual(self.state.scores["X"], 1)
        self.assertEqual(self.state.scores["O"], 0)

        # Further moves should be rejected
        self.assertFalse(self.state.make_move(5))

    def test_board_reset_preserves_scores(self):
        self.state.scores = {"X": 3, "O": 2}
        self.state.make_move(0)
        self.state.reset_board()

        self.assertEqual(self.state.board, [""] * 9)
        self.assertEqual(self.state.current_player, "X")
        self.assertFalse(self.state.game_over)
        self.assertIsNone(self.state.winning_line)
        self.assertEqual(self.state.scores, {"X": 3, "O": 2})

    def test_reset_scores(self):
        self.state.scores = {"X": 3, "O": 2}
        self.state.reset_scores()
        self.assertEqual(self.state.scores, {"X": 0, "O": 0})
        self.assertEqual(self.state.board, [""] * 9)


if __name__ == "__main__":
    unittest.main()
