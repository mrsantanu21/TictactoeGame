"""
Home Screen (Screen 1).
Clean, minimalist mobile home screen with decorative 3x3 board,
organic pastel background accents, and smooth navigation.
"""

import os
from kivy.graphics import Color, Line, Ellipse, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from components.rounded_button import RoundedButton, IconButton
from components.players_status_sheet import PlayersStatusSheet
from game.game_state import GameState


class DecorativeBoard(Widget):
    """
    Decorative 3x3 Tic-Tac-Toe board for Home screen.
    Displays:
      X | O | X
      O | X |
      O |   | X
    Drawn with smooth rounded line instructions.
    """

    DEMO_MARKS = ["X", "O", "X", "O", "X", "", "O", "", "X"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if self.width < 40 or self.height < 40:
            return

        t = theme_manager
        padding = min(self.width, self.height) * 0.08
        size = max(80.0, min(self.width, self.height) - padding * 2)
        x0 = self.x + (self.width - size) / 2.0
        y0 = self.y + (self.height - size) / 2.0
        cell = size / 3.0

        line_w = max(4.0, size * 0.024)
        mark_w = max(5.0, size * 0.038)
        mark_pad = cell * 0.28

        with self.canvas:
            # Sage green grid lines
            Color(*t.get("PRIMARY"))
            for i in (1, 2):
                vx = x0 + i * cell
                Line(points=[vx, y0 + 4, vx, y0 + size - 4], width=line_w, cap="round")
                hy = y0 + i * cell
                Line(points=[x0 + 4, hy, x0 + size - 4, hy], width=line_w, cap="round")

            # Demo marks
            for idx, mark in enumerate(self.DEMO_MARKS):
                if not mark:
                    continue
                row = idx // 3
                col = idx % 3
                inv_row = 2 - row
                cx = x0 + col * cell + cell / 2.0
                cy = y0 + inv_row * cell + cell / 2.0

                if mark == "X":
                    Color(*t.get("X_COLOR"))
                    Line(points=[cx - mark_pad, cy - mark_pad, cx + mark_pad, cy + mark_pad], width=mark_w, cap="round")
                    Line(points=[cx - mark_pad, cy + mark_pad, cx + mark_pad, cy - mark_pad], width=mark_w, cap="round")
                else:
                    Color(*t.get("O_COLOR"))
                    Line(circle=(cx, cy, mark_pad), width=mark_w)

    def _on_theme(self, tm):
        self._redraw()


class HomeScreen(Screen):
    """
    Screen 1: Mobile Home Screen.
    """

    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        # Background canvas with organic pastel shapes
        self.bg_widget = Widget(size_hint=(1, 1))
        self.bg_widget.bind(pos=self._draw_background, size=self._draw_background)
        self.root_layout.add_widget(self.bg_widget)

        # Main Vertical Layout
        self.content_layout = BoxLayout(
            orientation="vertical",
            padding=[24, 18, 24, 32],
            spacing=12,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.content_layout)

        # 1. TOP BAR
        top_bar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52)
        self.btn_menu = IconButton(icon="menu", on_click=self._open_status_sheet)
        self.btn_settings = IconButton(icon="gear", on_click=self._go_settings)
        top_bar.add_widget(self.btn_menu)
        top_bar.add_widget(Widget(size_hint_x=1))
        top_bar.add_widget(self.btn_settings)
        self.content_layout.add_widget(top_bar)

        # 2. TITLE
        self.title_lbl = Label(
            text="Tic Tac Toe",
            font_size="34sp",
            bold=True,
            size_hint=(1, None),
            height=60,
            halign="center",
            valign="middle",
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        self.content_layout.add_widget(self.title_lbl)

        # 3. CENTER DECORATIVE BOARD
        self.content_layout.add_widget(Widget(size_hint_y=0.08))
        self.board_widget = DecorativeBoard(size_hint=(1, 1))
        self.content_layout.add_widget(self.board_widget)

        # 4. TAGLINE
        self.tagline_lbl = Label(
            text="Think  •  Match  •  Win",
            font_size="15sp",
            size_hint=(1, None),
            height=36,
            halign="center",
            valign="middle",
        )
        self.tagline_lbl.bind(size=self.tagline_lbl.setter("text_size"))
        self.content_layout.add_widget(self.tagline_lbl)

        self.content_layout.add_widget(Widget(size_hint_y=0.15))

        # 5. BOTTOM NEW GAME BUTTON
        self.btn_new_game = RoundedButton(
            text="New Game",
            icon="play",
            style="primary",
            height=58,
            font_size="18sp",
            on_click=self._go_game_mode,
        )
        self.content_layout.add_widget(self.btn_new_game)

        # 6. Status Sheet modal
        self.status_sheet = PlayersStatusSheet(game_state=self.game_state)
        self.root_layout.add_widget(self.status_sheet)

        theme_manager.add_listener(self._on_theme)
        self._update_colors()

    def _draw_background(self, *args):
        self.bg_widget.canvas.clear()
        t = theme_manager
        w, h = self.width, self.height
        with self.bg_widget.canvas:
            Color(*t.get("BACKGROUND"))
            RoundedRectangle(pos=(0, 0), size=(w, h))

            # Subtle organic pastel curves/blobs
            Color(*t.get("PRIMARY_LIGHT"))
            # Top-left gentle curve
            Ellipse(pos=(-w * 0.35, h * 0.72), size=(w * 0.85, h * 0.42))
            # Bottom-right gentle curve
            Ellipse(pos=(w * 0.45, -h * 0.15), size=(w * 0.85, h * 0.45))

    def _update_colors(self):
        t = theme_manager
        self.title_lbl.color = t.get("PRIMARY_TEXT")
        self.tagline_lbl.color = t.get("SECONDARY_TEXT")
        self._draw_background()

    def _on_theme(self, tm):
        self._update_colors()

    def _open_status_sheet(self):
        self.status_sheet.open()

    def _go_settings(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "settings"

    def _go_game_mode(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "game_mode"
