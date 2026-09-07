"""
Score Screen (Screen 5).
Dedicated screen displaying Player X and Player O cumulative scores.
Includes Reset Scores with confirmation dialog.
"""

from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.dp_utils import dp, scaled_h
from components.rounded_button import RoundedButton, IconButton
from components.custom_dialogs import ConfirmDialog
from game.game_state import GameState


class ScoreRow(BoxLayout):
    """Single player score row: avatar + name + score value."""

    def __init__(self, mark: str, **kwargs):
        super().__init__(**kwargs)
        self.mark = mark
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = scaled_h(64)
        self.padding = [dp(16), dp(10), dp(16), dp(10)]
        self.spacing = dp(16)

        # Avatar circle — use dp() width so it scales with density
        self.avatar = Widget(size_hint=(None, 1), width=dp(44))
        self.avatar.bind(pos=self._draw_avatar, size=self._draw_avatar)
        self.add_widget(self.avatar)

        # Name label
        self.name_lbl = Label(
            text=f"Player {mark}",
            font_size="16sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        self.name_lbl.bind(size=self.name_lbl.setter("text_size"))
        self.add_widget(self.name_lbl)

        # Score value (right-aligned)
        self.score_lbl = Label(
            text="0",
            font_size="22sp",
            bold=True,
            halign="right",
            valign="middle",
            size_hint=(None, 1),
            width=dp(44),
        )
        self.score_lbl.bind(size=self.score_lbl.setter("text_size"))
        self.add_widget(self.score_lbl)

        theme_manager.add_listener(self._on_theme)
        self._update_colors()

    def _draw_avatar(self, *args):
        self.avatar.canvas.clear()
        t = theme_manager
        with self.avatar.canvas:
            if self.mark == "X":
                Color(*t.get("PRIMARY_TEXT"))
            else:
                Color(*t.get("PRIMARY"))
            pad = 4
            Ellipse(
                pos=(self.avatar.x + pad, self.avatar.y + pad),
                size=(self.avatar.width - pad * 2, self.avatar.height - pad * 2),
            )
            Color(1, 1, 1, 1)
            cx, cy = self.avatar.center_x, self.avatar.center_y
            p = 9
            if self.mark == "X":
                Line(points=[cx - p, cy - p, cx + p, cy + p], width=2.5, cap="round")
                Line(points=[cx - p, cy + p, cx + p, cy - p], width=2.5, cap="round")
            else:
                Line(circle=(cx, cy, p), width=2.5)

    def set_score(self, score: int) -> None:
        self.score_lbl.text = str(score)

    def _update_colors(self):
        t = theme_manager
        self.name_lbl.color = t.get("PRIMARY_TEXT")
        self.score_lbl.color = t.get("PRIMARY")
        self._draw_avatar()

    def _on_theme(self, tm):
        self._update_colors()


class ScoreScreen(Screen):
    """Screen 5: Score Screen."""

    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.confirm_dialog = None

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self.bg_widget = Widget(size_hint=(1, 1))
        self.bg_widget.bind(pos=self._draw_bg, size=self._draw_bg)
        self.root_layout.add_widget(self.bg_widget)

        self.content = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(18), dp(24), dp(32)],
            spacing=dp(20),
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.content)

        # HEADER
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=scaled_h(52))
        self.btn_back = IconButton(icon="back", on_click=self._go_back)
        header.add_widget(self.btn_back)
        self.header_title = Label(
            text="Score",
            font_size="20sp",
            bold=True,
            halign="center",
            valign="middle",
        )
        self.header_title.bind(size=self.header_title.setter("text_size"))
        header.add_widget(self.header_title)
        header.add_widget(Widget(size_hint=(None, 1), width=dp(44)))  # Balance spacer
        self.content.add_widget(header)

        self.content.add_widget(Widget(size_hint_y=0.06))

        # SCORE CARD
        self.score_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=scaled_h(158),
            spacing=0,
        )
        self.score_card.bind(pos=self._draw_score_card, size=self._draw_score_card)

        self.row_x = ScoreRow(mark="X")
        self.score_card.add_widget(self.row_x)

        self.divider = Widget(size_hint=(1, None), height=dp(1))
        self.divider.bind(pos=self._draw_divider, size=self._draw_divider)
        self.score_card.add_widget(self.divider)

        self.row_o = ScoreRow(mark="O")
        self.score_card.add_widget(self.row_o)

        self.content.add_widget(self.score_card)
        self.content.add_widget(Widget(size_hint_y=1))

        # RESET SCORES BUTTON
        self.btn_reset = RoundedButton(
            text="Reset Scores",
            style="surface",
            height=52,
            font_size="16sp",
            on_click=self._confirm_reset,
        )
        self.content.add_widget(self.btn_reset)

        self.game_state.add_listener(self._on_game_state_event)
        theme_manager.add_listener(self._on_theme)
        self._update_display()
        self._update_colors()

    def _draw_bg(self, *args):
        self.bg_widget.canvas.clear()
        t = theme_manager
        w, h = self.width, self.height
        with self.bg_widget.canvas:
            Color(*t.get("BACKGROUND"))
            RoundedRectangle(pos=(0, 0), size=(w, h))
            Color(*t.get("PRIMARY_LIGHT"))
            Ellipse(pos=(-w * 0.35, h * 0.72), size=(w * 0.85, h * 0.42))

    def _draw_score_card(self, *args):
        self.score_card.canvas.before.clear()
        t = theme_manager
        with self.score_card.canvas.before:
            Color(*t.get("SURFACE"))
            RoundedRectangle(pos=self.score_card.pos, size=self.score_card.size, radius=[20])
            Color(*t.get("BORDER"))
            Line(
                rounded_rectangle=(self.score_card.x, self.score_card.y,
                                   self.score_card.width, self.score_card.height, 20),
                width=1.1,
            )

    def _draw_divider(self, *args):
        self.divider.canvas.clear()
        t = theme_manager
        with self.divider.canvas:
            Color(*t.get("BORDER"))
            Line(
                points=[
                    self.divider.x + 16, self.divider.center_y,
                    self.divider.right - 16, self.divider.center_y,
                ],
                width=0.9,
            )

    def _update_display(self):
        self.row_x.set_score(self.game_state.scores.get("X", 0))
        self.row_o.set_score(self.game_state.scores.get("O", 0))

    def _update_colors(self):
        t = theme_manager
        self.header_title.color = t.get("PRIMARY_TEXT")
        self._draw_bg()
        self._draw_score_card()
        self._draw_divider()

    def _on_theme(self, tm):
        self._update_colors()

    def _on_game_state_event(self, event: str, state: GameState):
        self._update_display()

    def _confirm_reset(self):
        self.confirm_dialog = ConfirmDialog(
            title="Reset Scores?",
            message="This will set both scores back to 0.",
            on_confirm=self._do_reset,
        )
        self.confirm_dialog.show(self.root_layout)

    def _do_reset(self):
        self.game_state.reset_scores()
        self._update_display()

    def _go_back(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = self.manager.previous()
