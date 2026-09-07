"""
Game Mode Screen (Screen 2).
Mode selection between 'Player vs Player' and 'Player vs AI' (Coming Soon).
Matches Screen 2 of the design reference.
"""

from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.dp_utils import dp, scaled_h
from components.rounded_button import RoundedButton, IconButton, CanvasIcon
from game.game_state import GameState


class FloatingMarksWidget(Widget):
    """Subtle decorative floating X and O symbols in the center area."""

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
        with self.canvas:
            Color(*t.get("PRIMARY_LIGHT"))
            cx, cy = self.center_x, self.center_y

            # Small central O
            Line(circle=(cx - 40, cy + 10, 16), width=3)
            # Small central X
            p1 = 12
            Line(points=[cx + 40 - p1, cy - 20 - p1, cx + 40 + p1, cy - 20 + p1], width=3, cap="round")
            Line(points=[cx + 40 - p1, cy - 20 + p1, cx + 40 + p1, cy - 20 - p1], width=3, cap="round")

            # Faint background marks
            Color(*t.get("BORDER"))
            Line(circle=(cx + 60, cy + 50, 14), width=2)
            Line(points=[cx - 50 - 10, cy - 50 - 10, cx - 50 + 10, cy - 50 + 10], width=2, cap="round")
            Line(points=[cx - 50 - 10, cy - 50 + 10, cx - 50 + 10, cy - 50 - 10], width=2, cap="round")

    def _on_theme(self, tm):
        self._redraw()


class GameModeCard(BoxLayout):
    """
    Card for a game mode option.
    Option 1: Selected Player vs Player (primary color).
    Option 2: Disabled Player vs AI with 'Coming Soon' badge.
    """

    @staticmethod
    def _icon_key(symbol: str) -> str:
        """Map legacy emoji strings or icon names to CanvasIcon icon keys."""
        _map = {
            "👥": "people",
            "💻": "computer",
            "🏆": "trophy",
            "▶": "play",
            "people": "people",
            "computer": "computer",
        }
        return _map.get(symbol, symbol)

    def __init__(
        self,
        title: str,
        icon: str,
        is_selected: bool = False,
        is_disabled: bool = False,
        badge_text: str = "",
        on_tap=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = scaled_h(76)
        self.padding = [dp(20), dp(14), dp(20), dp(14)]
        self.spacing = dp(16)

        self.title_text = title
        self.icon_symbol = icon
        self.is_selected = is_selected
        self.is_disabled = is_disabled
        self.badge_text = badge_text
        self.on_tap = on_tap

        # Left Icon (canvas-drawn — no emoji glyph dependency)
        self.icon_widget = CanvasIcon(icon=self._icon_key(self.icon_symbol), size_dp=34)
        self.add_widget(self.icon_widget)

        # Title and optional badge column
        col = BoxLayout(orientation="vertical", spacing=2)
        self.title_lbl = Label(
            text=self.title_text,
            font_size="17sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        col.add_widget(self.title_lbl)

        if self.badge_text:
            self.badge_lbl = Label(
                text=self.badge_text,
                font_size="11.5sp",
                halign="left",
                valign="middle",
            )
            self.badge_lbl.bind(size=self.badge_lbl.setter("text_size"))
            col.add_widget(self.badge_lbl)
        else:
            self.badge_lbl = None

        self.add_widget(col)

        # Right indicator chevron
        self.chevron_lbl = Label(
            text="›",
            font_size="24sp",
            bold=True,
            size_hint=(None, 1),
            width=20,
            halign="center",
            valign="middle",
        )
        self.add_widget(self.chevron_lbl)

        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        t = theme_manager
        with self.canvas.before:
            if self.is_selected:
                # Forest green active card
                Color(*t.get("PRIMARY"))
                RoundedRectangle(pos=self.pos, size=self.size, radius=[22])
                fg = [1, 1, 1, 1] if not t.is_dark else [0.12, 0.14, 0.12, 1]
                sub_fg = [0.9, 0.9, 0.9, 1] if not t.is_dark else [0.22, 0.24, 0.22, 1]
            else:
                # Surface card
                Color(*t.get("SURFACE"))
                RoundedRectangle(pos=self.pos, size=self.size, radius=[22])
                Color(*t.get("BORDER"))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 22), width=1.1)
                fg = t.get("SECONDARY_TEXT") if self.is_disabled else t.get("PRIMARY_TEXT")
                sub_fg = t.get("SECONDARY_TEXT")

        self.icon_widget.set_color(fg)
        self.title_lbl.color = fg
        self.chevron_lbl.color = fg
        if self.badge_lbl:
            self.badge_lbl.color = sub_fg

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.is_disabled and self.on_tap:
                self.on_tap()
            return True
        return super().on_touch_down(touch)

    def _on_theme(self, tm):
        self._redraw()


class GameModeScreen(Screen):
    """
    Screen 2: Mobile Game Mode Screen.
    """

    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        # Background canvas with organic shapes
        self.bg_widget = Widget(size_hint=(1, 1))
        self.bg_widget.bind(pos=self._draw_bg, size=self._draw_bg)
        self.root_layout.add_widget(self.bg_widget)

        # Content container
        self.content_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(18), dp(24), dp(32)],
            spacing=dp(16),
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.content_layout)

        # 1. HEADER (Back | "Game Mode" | Settings)
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=scaled_h(52))
        self.btn_back = IconButton(icon="back", on_click=self._go_back)
        header.add_widget(self.btn_back)

        self.header_title = Label(
            text="Game Mode",
            font_size="20sp",
            bold=True,
            halign="center",
            valign="middle",
        )
        self.header_title.bind(size=self.header_title.setter("text_size"))
        header.add_widget(self.header_title)

        self.btn_settings = IconButton(icon="gear", on_click=self._go_settings)
        header.add_widget(self.btn_settings)
        self.content_layout.add_widget(header)

        self.content_layout.add_widget(Widget(size_hint_y=0.04))

        # 2. GAME MODE CARDS
        self.card_pvp = GameModeCard(
            title="Player vs Player",
            icon="people",
            is_selected=True,
            is_disabled=False,
            on_tap=self._select_pvp,
        )
        self.content_layout.add_widget(self.card_pvp)

        self.card_pva = GameModeCard(
            title="Player vs AI",
            icon="computer",
            is_selected=False,
            is_disabled=True,
            badge_text="Coming Soon",
        )
        self.content_layout.add_widget(self.card_pva)

        # 3. DECORATIVE FLOATING MARKS IN CENTER
        self.content_layout.add_widget(FloatingMarksWidget(size_hint=(1, 1)))

        # 4. BOTTOM START GAME BUTTON
        self.btn_start = RoundedButton(
            text="Start Game",
            icon="play",
            style="primary",
            height=58,
            font_size="18sp",
            on_click=self._go_gameplay,
        )
        self.content_layout.add_widget(self.btn_start)

        theme_manager.add_listener(self._on_theme)
        self._update_colors()

    def _draw_bg(self, *args):
        self.bg_widget.canvas.clear()
        t = theme_manager
        w, h = self.width, self.height
        with self.bg_widget.canvas:
            Color(*t.get("BACKGROUND"))
            RoundedRectangle(pos=(0, 0), size=(w, h))

            # Bottom-right pastel curve
            Color(*t.get("PRIMARY_LIGHT"))
            Ellipse(pos=(w * 0.45, -h * 0.15), size=(w * 0.85, h * 0.45))

    def _update_colors(self):
        t = theme_manager
        self.header_title.color = t.get("PRIMARY_TEXT")
        self._draw_bg()

    def _on_theme(self, tm):
        self._update_colors()

    def _select_pvp(self):
        self.card_pvp.set_selected(True)
        self.game_state.set_game_mode("pvp")

    def _go_back(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "home"

    def _go_settings(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "settings"

    def _go_gameplay(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "gameplay"
