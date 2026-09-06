"""
Pure Tic-Tac-Toe Game Logic.
Preserves original algorithms from the Windows desktop application.
Independent of UI and frameworks.
"""

from typing import List, Optional, Tuple

WINNING_COMBINATIONS: List[Tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical
    (0, 4, 8), (2, 4, 6),              # Diagonal
]


def check_winner(board: List[str]) -> Optional[Tuple[int, int, int]]:
    """
    Checks if there is a winner on the 3x3 board.
    Returns the winning tuple (a, b, c) if won, otherwise None.
    """
    if len(board) != 9:
        return None
    for combo in WINNING_COMBINATIONS:
        a, b, c = combo
        if board[a] != "" and board[a] == board[b] == board[c]:
            return combo
    return None


def check_draw(board: List[str], winning_line: Optional[Tuple[int, int, int]] = None) -> bool:
    """
    Checks if the game has ended in a draw.
    A draw occurs when all 9 cells are filled and no winning combination exists.
    """
    if len(board) != 9:
        return False
    if winning_line is not None:
        return False
    if check_winner(board) is not None:
        return False
    return all(cell != "" for cell in board)


def is_valid_move(board: List[str], position: int) -> bool:
    """
    Determines if a move is valid at the specified position (0-8).
    """
    if not isinstance(position, int) or position < 0 or position >= 9:
        return False
    return board[position] == ""


def get_available_moves(board: List[str]) -> List[int]:
    """
    Returns a list of empty cell indices (0-8).
    """
    return [i for i, cell in enumerate(board) if cell == ""]
