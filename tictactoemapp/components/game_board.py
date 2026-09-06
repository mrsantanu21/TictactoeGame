"""
Mobile Game Board Component.
Responsive square 3x3 Tic-Tac-Toe canvas board with smooth rounded lines,
canvas-drawn X and O marks with scale animations, and winning strike-through line.
Strictly contains only two vertical and two horizontal lines without rectangular borders.
"""

from typing import Callable, Dict, Optional, Tuple
from kivy.animation import Animation
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.sound_manager import sound_manager
from game.game_state import GameState


class AnimatedCell(Widget):
    """Auxiliary widget for animating mark scale."""
    scale = NumericProperty(1.0)


class MobileGameBoard(Widget):
    """
    3x3 Tic-Tac-Toe board rendered purely via Kivy canvas instructions.
    Responsive square sizing centered within available space.
    """

    def __init__(self, game_state: Optional[GameState] = None, on_cell_tap: Optional[Callable[[int], None]] = None, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.on_cell_tap = on_cell_tap

        # Animation scales for placed marks: index -> scale float (0.0 to 1.0)
        self.mark_scales: Dict[int, float] = {i: 1.0 for i in range(9)}
        self._animated_cells: Dict[int, AnimatedCell] = {}
        self._prev_board = [""] * 9

        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        if self.game_state:
            self.game_state.add_listener(self._on_game_state_event)

        self._redraw()

    def set_game_state(self, game_state: GameState) -> None:
        if self.game_state:
            self.game_state.remove_listener(self._on_game_state_event)
        self.game_state = game_state
        self.game_state.add_listener(self._on_game_state_event)
        self._prev_board = list(self.game_state.board)
        self._redraw()

    def _get_board_geometry(self) -> Tuple[float, float, float]:
        """Calculates centered square board bounds: (x0, y0, size)."""
        padding = min(self.width, self.height) * 0.08
        size = max(100.0, min(self.width, self.height) - padding * 2)
        x0 = self.x + (self.width - size) / 2.0
        y0 = self.y + (self.height - size) / 2.0
        return x0, y0, size

    def _get_cell_center(self, index: int, x0: float, y0: float, size: float) -> Tuple[float, float]:
        """Maps board index 0-8 to canvas (cx, cy). Index 0 is top-left, 8 is bottom-right."""
        cell_size = size / 3.0
        row = index // 3       # 0 (top), 1 (mid), 2 (bottom)
        col = index % 3        # 0 (left), 1 (mid), 2 (right)
        inv_row = 2 - row      # In Kivy, y=0 is bottom, so top row is row index 2 from bottom
        cx = x0 + col * cell_size + cell_size / 2.0
        cy = y0 + inv_row * cell_size + cell_size / 2.0
        return cx, cy

    def _redraw(self, *args) -> None:
        self.canvas.clear()
        if not self.game_state or self.width < 50 or self.height < 50:
            return

        t = theme_manager
        x0, y0, size = self._get_board_geometry()
        cell_size = size / 3.0

        line_width = max(5.0, size * 0.024)
        mark_width = max(6.0, size * 0.038)

        with self.canvas:
            # ----------------------------------------------------------------
            # 1. The 4 Grid Lines (Two vertical, two horizontal)
            # Smooth rounded line caps, sage green primary color
            # ----------------------------------------------------------------
            Color(*t.get("PRIMARY"))

            # Two vertical lines
            for i in (1, 2):
                vx = x0 + i * cell_size
                Line(
                    points=[vx, y0, vx, y0 + size],
                    width=line_width,
                    cap="round",
                    joint="round",
                )

            # Two horizontal lines
            for i in (1, 2):
                hy = y0 + i * cell_size
                Line(
                    points=[x0, hy, x0 + size, hy],
                    width=line_width,
                    cap="round",
                    joint="round",
                )

            # ----------------------------------------------------------------
            # 2. X and O Marks
            # Canvas instructions with scale animation and winning color highlight
            # ----------------------------------------------------------------
            winning_line = self.game_state.winning_line

            for idx, val in enumerate(self.game_state.board):
                if not val:
                    continue

                cx, cy = self._get_cell_center(idx, x0, y0, size)
                is_win_cell = winning_line is not None and idx in winning_line
                scale = self.mark_scales.get(idx, 1.0)
                pad = (cell_size * 0.28) * scale

                if is_win_cell:
                    Color(*t.get("WINNING_ACCENT"))
                elif val == "X":
                    Color(*t.get("X_COLOR"))
                else:
                    Color(*t.get("O_COLOR"))

                if val == "X":
                    Line(
                        points=[cx - pad, cy - pad, cx + pad, cy + pad],
                        width=mark_width,
                        cap="round",
                    )
                    Line(
                        points=[cx - pad, cy + pad, cx + pad, cy - pad],
                        width=mark_width,
                        cap="round",
                    )
                else:
                    Line(
                        circle=(cx, cy, pad),
                        width=mark_width,
                    )

            # ----------------------------------------------------------------
            # 3. Winning Line Strike-Through
            # ----------------------------------------------------------------
            if winning_line:
                a, _, c = winning_line
                ax, ay = self._get_cell_center(a, x0, y0, size)
                cx_c, cy_c = self._get_cell_center(c, x0, y0, size)

                # Extend slightly past cell centers for visual elegance
                dx = cx_c - ax
                dy = cy_c - ay
                ext = 0.15
                p1_x = ax - dx * ext
                p1_y = ay - dy * ext
                p2_x = cx_c + dx * ext
                p2_y = cy_c + dy * ext

                Color(*t.get("WINNING_ACCENT"))
                Line(
                    points=[p1_x, p1_y, p2_x, p2_y],
                    width=line_width * 1.25,
                    cap="round",
                )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if not self.game_state or self.game_state.game_over:
            return True

        x0, y0, size = self._get_board_geometry()
        if not (x0 <= touch.x <= x0 + size and y0 <= touch.y <= y0 + size):
            return True

        cell_size = size / 3.0
        col = int((touch.x - x0) // cell_size)
        inv_row = int((touch.y - y0) // cell_size)
        col = min(max(col, 0), 2)
        inv_row = min(max(inv_row, 0), 2)
        row = 2 - inv_row
        cell_index = row * 3 + col

        if self.game_state.board[cell_index] == "":
            mark = self.game_state.current_player
            if self.on_cell_tap:
                self.on_cell_tap(cell_index)
            else:
                self.game_state.make_move(cell_index)

            # Trigger mark sound
            sound_manager.play(f"move_{mark.lower()}")

        return True

    def _animate_mark(self, index: int) -> None:
        """Subtle smooth scale-in animation for the placed mark."""
        self.mark_scales[index] = 0.2
        anim_widget = AnimatedCell(scale=0.2)
        self._animated_cells[index] = anim_widget

        def update_scale(inst, value):
            self.mark_scales[index] = value
            self._redraw()

        anim_widget.bind(scale=update_scale)
        anim = Animation(scale=1.0, duration=0.18, t="out_quad")
        anim.start(anim_widget)

    def _on_game_state_event(self, event: str, state: GameState) -> None:
        if event == "move_made":
            for i in range(9):
                if state.board[i] != "" and self._prev_board[i] == "":
                    self._animate_mark(i)
            self._prev_board = list(state.board)
        elif event == "board_reset":
            self.mark_scales = {i: 1.0 for i in range(9)}
            self._prev_board = [""] * 9
        elif event == "game_won":
            sound_manager.play("win")
        elif event == "game_draw":
            sound_manager.play("draw")

        self._redraw()

    def _on_theme(self, tm):
        self._redraw()
