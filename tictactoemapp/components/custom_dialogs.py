"""
Custom Mobile Dialogs Component.
Modern modal popups for Game Over ('Play Again' & 'Home') and Score Reset confirmation.
Follows the rounded cream, sage-green, and soft-shadow visual identity.
"""

from typing import Callable, Optional
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.dp_utils import dp, scaled_h
from .rounded_button import RoundedButton


class GameOverDialog(FloatLayout):
    """
    Game Over modal popup.
    Displays outcome celebration ("Player X Wins! 🎉" or "It's a Draw!").
    Actions: "Play Again" and "Home".
    """

    def __init__(
        self,
        title: str = "Player X Wins!",
        subtitle: str = "Outstanding match! Ready for another round?",
        on_play_again: Optional[Callable[[], None]] = None,
        on_home: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {"x": 0, "y": 0}
        self.on_play_again = on_play_again
        self.on_home = on_home

        # Dark overlay
        self.overlay = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.overlay.bind(pos=self._draw_overlay, size=self._draw_overlay)
        self.add_widget(self.overlay)

        # Center card — height scales with screen viewport
        self.card = BoxLayout(
            orientation="vertical",
            size_hint=(0.88, None),
            height=scaled_h(280),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=dp(16),
            padding=[dp(24), dp(28), dp(24), dp(24)],
        )
        self.card.bind(pos=self._draw_card, size=self._draw_card)
        self.add_widget(self.card)

        # Content
        self.title_lbl = Label(
            text=title,
            font_size="22sp",
            bold=True,
            size_hint=(1, None),
            height=scaled_h(34),
            halign="center",
            valign="middle",
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        self.card.add_widget(self.title_lbl)

        self.sub_lbl = Label(
            text=subtitle,
            font_size="14sp",
            size_hint=(1, None),
            height=scaled_h(40),
            halign="center",
            valign="middle",
        )
        self.sub_lbl.bind(size=self.sub_lbl.setter("text_size"))
        self.card.add_widget(self.sub_lbl)

        self.card.add_widget(Widget(size_hint_y=0.1))

        # Buttons
        self.btn_play_again = RoundedButton(
            text="Play Again",
            icon="play",
            style="primary",
            height=50,
            on_click=self._handle_play_again,
        )
        self.card.add_widget(self.btn_play_again)

        self.btn_home = RoundedButton(
            text="Home",
            style="surface",
            height=46,
            on_click=self._handle_home,
        )
        self.card.add_widget(self.btn_home)

        self.bind(pos=self._center_card, size=self._center_card)
        theme_manager.add_listener(self._on_theme)
        self._center_card()
        self._update_colors()

    def set_result(self, winner: Optional[str] = None, is_draw: bool = False) -> None:
        if is_draw:
            self.title_lbl.text = "It's a Draw!"
            self.sub_lbl.text = "Both played exceptionally well."
        elif winner:
            self.title_lbl.text = f"Player {winner} Wins!"
            self.sub_lbl.text = "Victory belongs to " + ("You!" if winner == "X" else "Player O!")
        else:
            self.title_lbl.text = "Game Finished"
            self.sub_lbl.text = "Care to play again?"

    def _center_card(self, *args):
        self._draw_overlay()
        self._draw_card()

    def _draw_overlay(self, *args):
        self.overlay.canvas.clear()
        t = theme_manager
        with self.overlay.canvas:
            Color(*t.get("OVERLAY"))
            RoundedRectangle(pos=self.pos, size=self.size)

    def _draw_card(self, *args):
        self.card.canvas.before.clear()
        t = theme_manager
        with self.card.canvas.before:
            Color(*t.get("SURFACE"))
            RoundedRectangle(pos=self.card.pos, size=self.card.size, radius=[24])
            Color(*t.get("BORDER"))
            Line(
                rounded_rectangle=(self.card.x, self.card.y, self.card.width, self.card.height, 24),
                width=1.2,
            )

    def _update_colors(self):
        t = theme_manager
        self.title_lbl.color = t.get("PRIMARY_TEXT")
        self.sub_lbl.color = t.get("SECONDARY_TEXT")

    def _on_theme(self, tm):
        self._center_card()
        self._update_colors()

    def _handle_play_again(self):
        self.dismiss()
        if self.on_play_again:
            self.on_play_again()

    def _handle_home(self):
        self.dismiss()
        if self.on_home:
            self.on_home()

    def show(self, parent_widget):
        if self.parent is None:
            self.opacity = 0
            self.size = parent_widget.size
            self.pos = parent_widget.pos
            parent_widget.add_widget(self)
            self.do_layout()
            self._center_card()
            anim = Animation(opacity=1, duration=0.2)
            anim.start(self)

    def dismiss(self):
        if self.parent:
            anim = Animation(opacity=0, duration=0.15)

            def remove(*args):
                if self.parent:
                    self.parent.remove_widget(self)

            anim.bind(on_complete=remove)
            anim.start(self)


class ConfirmDialog(FloatLayout):
    """
    Confirmation modal for destructive actions like 'Reset Scores'.
    """

    def __init__(
        self,
        title: str = "Reset Scores?",
        message: str = "This will set both Player X and Player O scores back to 0.",
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {"x": 0, "y": 0}
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.overlay = Widget(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.overlay.bind(pos=self._draw_overlay, size=self._draw_overlay)
        self.add_widget(self.overlay)

        self.card = BoxLayout(
            orientation="vertical",
            size_hint=(0.88, None),
            height=scaled_h(210),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=dp(14),
            padding=[dp(20), dp(22), dp(20), dp(20)],
        )
        self.card.bind(pos=self._draw_card, size=self._draw_card)
        self.add_widget(self.card)

        self.title_lbl = Label(
            text=title,
            font_size="20sp",
            bold=True,
            size_hint=(1, None),
            height=scaled_h(30),
            halign="center",
            valign="middle",
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        self.card.add_widget(self.title_lbl)

        self.msg_lbl = Label(
            text=message,
            font_size="13.5sp",
            size_hint=(1, None),
            height=scaled_h(38),
            halign="center",
            valign="middle",
        )
        self.msg_lbl.bind(size=self.msg_lbl.setter("text_size"))
        self.card.add_widget(self.msg_lbl)

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=scaled_h(46))
        self.btn_cancel = RoundedButton(
            text="Cancel",
            style="surface",
            height=46,
            on_click=self._handle_cancel,
        )
        btn_row.add_widget(self.btn_cancel)

        self.btn_confirm = RoundedButton(
            text="Reset",
            style="primary",
            height=46,
            on_click=self._handle_confirm,
        )
        btn_row.add_widget(self.btn_confirm)
        self.card.add_widget(btn_row)

        self.bind(pos=self._center_card, size=self._center_card)
        theme_manager.add_listener(self._on_theme)
        self._center_card()
        self._update_colors()

    def _center_card(self, *args):
        self._draw_overlay()
        self._draw_card()

    def _draw_overlay(self, *args):
        self.overlay.canvas.clear()
        t = theme_manager
        with self.overlay.canvas:
            Color(*t.get("OVERLAY"))
            RoundedRectangle(pos=self.pos, size=self.size)

    def _draw_card(self, *args):
        self.card.canvas.before.clear()
        t = theme_manager
        with self.card.canvas.before:
            Color(*t.get("SURFACE"))
            RoundedRectangle(pos=self.card.pos, size=self.card.size, radius=[22])
            Color(*t.get("BORDER"))
            Line(
                rounded_rectangle=(self.card.x, self.card.y, self.card.width, self.card.height, 22),
                width=1.2,
            )

    def _update_colors(self):
        t = theme_manager
        self.title_lbl.color = t.get("PRIMARY_TEXT")
        self.msg_lbl.color = t.get("SECONDARY_TEXT")

    def _on_theme(self, tm):
        self._center_card()
        self._update_colors()

    def _handle_cancel(self):
        self.dismiss()
        if self.on_cancel:
            self.on_cancel()

    def _handle_confirm(self):
        self.dismiss()
        if self.on_confirm:
            self.on_confirm()

    def show(self, parent_widget):
        if self.parent is None:
            self.opacity = 0
            self.size = parent_widget.size
            self.pos = parent_widget.pos
            parent_widget.add_widget(self)
            self.do_layout()
            self._center_card()
            anim = Animation(opacity=1, duration=0.18)
            anim.start(self)

    def dismiss(self):
        if self.parent:
            anim = Animation(opacity=0, duration=0.15)

            def remove(*args):
                if self.parent:
                    self.parent.remove_widget(self)

            anim.bind(on_complete=remove)
            anim.start(self)
