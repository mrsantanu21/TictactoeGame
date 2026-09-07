"""
Player Header Card Component.
Displays Player X ('You') and Player O ('Opponent') horizontally with turn highlight and avatars.
Matches Screen 3 of the design specification.
"""

from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.dp_utils import dp, scaled_h


class CircularAvatar(Widget):
    """Circular avatar displaying either an X or O symbol with canvas drawing."""

    def __init__(self, mark: str = "X", is_active: bool = False, size_dp: float = 46.0, **kwargs):
        super().__init__(**kwargs)
        self.mark = mark
        self.is_active = is_active
        self.size_hint = (None, None)
        # Use dp() so the avatar circle scales with screen density
        _sz = dp(size_dp)
        self.size = (_sz, _sz)
        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        t = theme_manager
        with self.canvas:
            # Circle background: X = dark charcoal, O = sage green
            if self.mark == "X":
                Color(*t.get("PRIMARY_TEXT"))
            else:
                Color(*t.get("PRIMARY"))

            Ellipse(pos=self.pos, size=self.size)

            # Draw mark symbol (white on circle)
            Color(1, 1, 1, 1)
            cx, cy = self.center_x, self.center_y
            pad = self.width * 0.28
            stroke_w = max(2.5, self.width * 0.08)

            if self.mark == "X":
                Line(points=[cx - pad, cy - pad, cx + pad, cy + pad], width=stroke_w, cap="round")
                Line(points=[cx - pad, cy + pad, cx + pad, cy - pad], width=stroke_w, cap="round")
            else:
                Line(circle=(cx, cy, pad), width=stroke_w)

    def _on_theme(self, tm):
        self._redraw()


class PlayerItem(BoxLayout):
    """Single player column: avatar, name label, subtitle, and active indicator dot."""

    def __init__(self, mark: str, name: str, subtitle: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.mark = mark

        self.avatar = CircularAvatar(mark=mark, size_dp=42.0)
        self.add_widget(self.avatar)

        # Labels box
        lbl_box = BoxLayout(orientation="vertical", spacing=dp(2))
        self.name_lbl = Label(
            text=name,
            font_size="15sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        self.name_lbl.bind(size=self.name_lbl.setter("text_size"))
        lbl_box.add_widget(self.name_lbl)

        self.sub_lbl = Label(
            text=subtitle,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        self.sub_lbl.bind(size=self.sub_lbl.setter("text_size"))
        lbl_box.add_widget(self.sub_lbl)

        self.add_widget(lbl_box)

        self.is_active = False
        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.avatar.set_active(active)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        t = theme_manager
        with self.canvas.before:
            if self.is_active:
                # Soft active pill background
                Color(*t.get("PRIMARY_LIGHT"))
                RoundedRectangle(
                    pos=(self.x + 4, self.y + 4),
                    size=(self.width - 8, self.height - 8),
                    radius=[16],
                )

        # Label colors
        self.name_lbl.color = t.get("PRIMARY_TEXT")
        self.sub_lbl.color = t.get("SECONDARY_TEXT")

    def _on_theme(self, tm):
        self._redraw()


class PlayerHeaderCard(BoxLayout):
    """
    Rounded horizontal card hosting both Player X and Player O.
    Includes thin central vertical divider.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        # Scale card height with screen viewport so it's proportional on all phones
        self.height = scaled_h(76)
        self.padding = [dp(6), dp(6), dp(6), dp(6)]
        self.spacing = dp(4)

        self.player_x_item = PlayerItem(mark="X", name="Player X", subtitle="You")
        self.add_widget(self.player_x_item)

        # Central divider
        self.divider = Widget(size_hint=(None, 1), width=dp(1.5))
        self.divider.bind(pos=self._draw_divider, size=self._draw_divider)
        self.add_widget(self.divider)

        self.player_o_item = PlayerItem(mark="O", name="Player O", subtitle="Opponent")
        self.add_widget(self.player_o_item)

        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def set_current_player(self, current_player: str) -> None:
        self.player_x_item.set_active(current_player == "X")
        self.player_o_item.set_active(current_player == "O")

    def _draw_divider(self, *args):
        self.divider.canvas.clear()
        t = theme_manager
        with self.divider.canvas:
            Color(*t.get("BORDER"))
            Line(
                points=[
                    self.divider.center_x,
                    self.divider.y + 14,
                    self.divider.center_x,
                    self.divider.top - 14,
                ],
                width=1.2,
            )

    def _redraw(self, *args):
        self.canvas.before.clear()
        t = theme_manager
        with self.canvas.before:
            # Card background
            Color(*t.get("SURFACE"))
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[20],
            )
            # Subtle card outline
            Color(*t.get("BORDER"))
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, 20),
                width=1.0,
            )
        self._draw_divider()

    def _on_theme(self, tm):
        self._redraw()
