"""
Players and Game Status Bottom Sheet Component.
A modal bottom sheet panel that slides up over a darkened background overlay.
Matches Screen 4 of the design reference.
"""

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.dp_utils import dp, sh, clamp, scaled_h
from game.game_state import GameState
from components.rounded_button import CanvasIcon


class StatusIndicatorDot(Widget):
    """Small circular status dot: active green when player's turn, neutral gray otherwise."""

    def __init__(self, is_active: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_active = is_active
        self.size_hint = (None, None)
        # Use dp() so status dot scales with screen density
        _sz = dp(14)
        self.size = (_sz, _sz)
        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def set_active(self, active: bool):
        self.is_active = active
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        t = theme_manager
        with self.canvas:
            if self.is_active:
                Color(*t.get("PRIMARY"))
            else:
                Color(*t.get("BORDER"))
            Ellipse(pos=self.pos, size=self.size)

    def _on_theme(self, tm):
        self._redraw()


class PlayersStatusSheet(FloatLayout):
    """
    Bottom Sheet modal panel displaying Players status and dynamic Game Status card.
    Slides up from bottom on open(), dismisses on background tap or close().
    """

    def __init__(self, game_state: GameState, on_dismiss=None, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state
        self.on_dismiss = on_dismiss
        self.is_open = False

        # Semi-transparent backdrop overlay
        self.backdrop = Widget(size_hint=(1, 1))
        self.backdrop.bind(pos=self._draw_backdrop, size=self._draw_backdrop)
        self.add_widget(self.backdrop)

        # Bottom Sheet container
        # Use sh() so the sheet occupies a proportional fraction of any screen height,
        # clamped between 300 and 520 dp so it never overflows tiny or huge screens.
        _panel_h = clamp(sh(0.60), dp(300), dp(520))
        self.panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=_panel_h,
            y=-_panel_h,  # Starts hidden below the screen
            spacing=dp(16),
            padding=[dp(24), dp(16), dp(24), dp(28)],
        )
        self.panel.bind(pos=self._draw_panel, size=self._draw_panel)
        self.add_widget(self.panel)

        self._build_content()

        self.bind(pos=self._on_layout_change, size=self._on_layout_change)
        theme_manager.add_listener(self._on_theme)
        if self.game_state:
            self.game_state.add_listener(self._on_game_state_event)

        # Initially invisible
        self.opacity = 0
        self.disabled = True

    def _build_content(self):
        # 1. Subtle Drag Indicator Handle
        handle_container = BoxLayout(size_hint=(1, None), height=dp(14))
        self.handle = Widget(size_hint=(None, None), size=(dp(44), dp(5)))
        self.handle.bind(pos=self._draw_handle, size=self._draw_handle)
        handle_container.add_widget(Widget(size_hint_x=0.5))
        handle_container.add_widget(self.handle)
        handle_container.add_widget(Widget(size_hint_x=0.5))
        self.panel.add_widget(handle_container)

        # 2. Section Title: "Players"
        self.players_title = Label(
            text="Players",
            font_size="19sp",
            bold=True,
            size_hint=(1, None),
            height=scaled_h(28),
            halign="left",
            valign="middle",
        )
        self.players_title.bind(size=self.players_title.setter("text_size"))
        self.panel.add_widget(self.players_title)

        # 3. Players Rounded Card
        self.players_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=scaled_h(130),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
        )
        self.players_card.bind(pos=self._draw_players_card, size=self._draw_players_card)

        # Player X Row
        row_x = BoxLayout(orientation="horizontal", spacing=dp(12))
        self.avatar_x = self._create_avatar("X")
        row_x.add_widget(self.avatar_x)

        info_x = BoxLayout(orientation="vertical", spacing=dp(2))
        self.lbl_x_name = Label(text="Player X", font_size="15sp", bold=True, halign="left", valign="middle")
        self.lbl_x_name.bind(size=self.lbl_x_name.setter("text_size"))
        self.lbl_x_sub = Label(text="You", font_size="12sp", halign="left", valign="middle")
        self.lbl_x_sub.bind(size=self.lbl_x_sub.setter("text_size"))
        info_x.add_widget(self.lbl_x_name)
        info_x.add_widget(self.lbl_x_sub)
        row_x.add_widget(info_x)

        self.dot_x = StatusIndicatorDot(is_active=True)
        row_x.add_widget(self.dot_x)
        self.players_card.add_widget(row_x)

        # Divider line
        self.card_divider = Widget(size_hint=(1, None), height=1)
        self.card_divider.bind(pos=self._draw_card_divider, size=self._draw_card_divider)
        self.players_card.add_widget(self.card_divider)

        # Player O Row
        row_o = BoxLayout(orientation="horizontal", spacing=dp(12))
        self.avatar_o = self._create_avatar("O")
        row_o.add_widget(self.avatar_o)

        info_o = BoxLayout(orientation="vertical", spacing=dp(2))
        self.lbl_o_name = Label(text="Player O", font_size="15sp", bold=True, halign="left", valign="middle")
        self.lbl_o_name.bind(size=self.lbl_o_name.setter("text_size"))
        self.lbl_o_sub = Label(text="Opponent", font_size="12sp", halign="left", valign="middle")
        self.lbl_o_sub.bind(size=self.lbl_o_sub.setter("text_size"))
        info_o.add_widget(self.lbl_o_name)
        info_o.add_widget(self.lbl_o_sub)
        row_o.add_widget(info_o)

        self.dot_o = StatusIndicatorDot(is_active=False)
        row_o.add_widget(self.dot_o)
        self.players_card.add_widget(row_o)

        self.panel.add_widget(self.players_card)

        # 4. Section Title: "Game Status"
        self.status_title = Label(
            text="Game Status",
            font_size="17sp",
            bold=True,
            size_hint=(1, None),
            height=scaled_h(26),
            halign="left",
            valign="middle",
        )
        self.status_title.bind(size=self.status_title.setter("text_size"))
        self.panel.add_widget(self.status_title)

        # 5. Rounded Soft Pastel-Green Status Card
        self.status_card = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=scaled_h(58),
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(12),
        )
        self.status_card.bind(pos=self._draw_status_card, size=self._draw_status_card)

        self.status_icon = CanvasIcon(
            icon="game",
            size_dp=26,
        )
        self.status_card.add_widget(self.status_icon)

        self.status_lbl = Label(
            text="Player X's Turn",
            font_size="16sp",
            bold=True,
            halign="left",
            valign="middle",
        )
        self.status_lbl.bind(size=self.status_lbl.setter("text_size"))
        self.status_card.add_widget(self.status_lbl)

        self.panel.add_widget(self.status_card)
        self._update_colors()

    def _create_avatar(self, mark: str) -> Widget:
        _sz = dp(38)
        widget = Widget(size_hint=(None, None), size=(_sz, _sz))

        def draw(w, *args):
            w.canvas.clear()
            t = theme_manager
            with w.canvas:
                if mark == "X":
                    Color(*t.get("PRIMARY_TEXT"))
                else:
                    Color(*t.get("PRIMARY"))
                Ellipse(pos=w.pos, size=w.size)

                Color(1, 1, 1, 1)
                cx, cy = w.center_x, w.center_y
                p = 10
                if mark == "X":
                    Line(points=[cx - p, cy - p, cx + p, cy + p], width=2.5, cap="round")
                    Line(points=[cx - p, cy + p, cx + p, cy - p], width=2.5, cap="round")
                else:
                    Line(circle=(cx, cy, p), width=2.5)

        widget.bind(pos=draw, size=draw)
        theme_manager.add_listener(lambda tm: draw(widget))
        return widget

    def _draw_backdrop(self, *args):
        self.backdrop.canvas.clear()
        t = theme_manager
        with self.backdrop.canvas:
            Color(*t.get("OVERLAY"))
            RoundedRectangle(pos=self.pos, size=self.size)

    def _draw_panel(self, *args):
        self.panel.canvas.before.clear()
        t = theme_manager
        with self.panel.canvas.before:
            Color(*t.get("BACKGROUND"))
            RoundedRectangle(
                pos=self.panel.pos,
                size=self.panel.size,
                radius=[28, 28, 0, 0],
            )

    def _draw_handle(self, *args):
        self.handle.canvas.clear()
        t = theme_manager
        with self.handle.canvas:
            Color(*t.get("BORDER"))
            RoundedRectangle(
                pos=self.handle.pos,
                size=self.handle.size,
                radius=[2.5],
            )

    def _draw_players_card(self, *args):
        self.players_card.canvas.before.clear()
        t = theme_manager
        with self.players_card.canvas.before:
            Color(*t.get("SURFACE"))
            RoundedRectangle(
                pos=self.players_card.pos,
                size=self.players_card.size,
                radius=[18],
            )
            Color(*t.get("BORDER"))
            Line(
                rounded_rectangle=(self.players_card.x, self.players_card.y, self.players_card.width, self.players_card.height, 18),
                width=1.0,
            )

    def _draw_card_divider(self, *args):
        self.card_divider.canvas.clear()
        t = theme_manager
        with self.card_divider.canvas:
            Color(*t.get("BORDER"))
            Line(
                points=[
                    self.card_divider.x,
                    self.card_divider.center_y,
                    self.card_divider.right,
                    self.card_divider.center_y,
                ],
                width=0.8,
            )

    def _draw_status_card(self, *args):
        self.status_card.canvas.before.clear()
        t = theme_manager
        with self.status_card.canvas.before:
            # Soft pastel-green background
            Color(*t.get("PRIMARY_LIGHT"))
            RoundedRectangle(
                pos=self.status_card.pos,
                size=self.status_card.size,
                radius=[16],
            )

    def _update_colors(self):
        t = theme_manager
        self.players_title.color = t.get("PRIMARY_TEXT")
        self.lbl_x_name.color = t.get("PRIMARY_TEXT")
        self.lbl_x_sub.color = t.get("SECONDARY_TEXT")
        self.lbl_o_name.color = t.get("PRIMARY_TEXT")
        self.lbl_o_sub.color = t.get("SECONDARY_TEXT")
        self.status_title.color = t.get("PRIMARY_TEXT")
        self.status_lbl.color = t.get("PRIMARY_TEXT")
        self._update_status_display()

    def _update_status_display(self):
        if not self.game_state:
            return
        if self.game_state.winning_line:
            self.status_lbl.text = f"Player {self.game_state.current_player} Wins!"
            self.status_icon.icon_type = "trophy"
            self.status_icon._redraw()
            self.dot_x.set_active(False)
            self.dot_o.set_active(False)
        elif self.game_state.game_over:
            self.status_lbl.text = "It's a Draw!"
            self.status_icon.icon_type = "check"
            self.status_icon._redraw()
            self.dot_x.set_active(False)
            self.dot_o.set_active(False)
        else:
            self.status_lbl.text = f"Player {self.game_state.current_player}'s Turn"
            self.status_icon.icon_type = "game"
            self.status_icon._redraw()
            self.dot_x.set_active(self.game_state.current_player == "X")
            self.dot_o.set_active(self.game_state.current_player == "O")

    def open(self):
        """Slides up bottom sheet with smooth animation."""
        self._update_status_display()
        self.opacity = 1
        self.disabled = False
        self.is_open = True
        anim = Animation(y=0, duration=0.25, t="out_quad")
        anim.start(self.panel)

    def dismiss(self):
        """Slides down bottom sheet and hides overlay."""
        if not self.is_open:
            return
        self.is_open = False
        anim = Animation(y=-self.panel.height, duration=0.2, t="in_quad")

        def on_finish(*args):
            self.opacity = 0
            self.disabled = True
            if self.on_dismiss:
                self.on_dismiss()

        anim.bind(on_complete=on_finish)
        anim.start(self.panel)

    def on_touch_down(self, touch):
        if not self.is_open:
            return False
        # If touch is outside the bottom panel, dismiss sheet
        if not self.panel.collide_point(*touch.pos):
            self.dismiss()
            return True
        return super().on_touch_down(touch)

    def _on_layout_change(self, *args):
        self._draw_backdrop()
        if not self.is_open:
            self.panel.y = -self.panel.height

    def _on_theme(self, tm):
        self._draw_backdrop()
        self._draw_panel()
        self._draw_handle()
        self._draw_players_card()
        self._draw_card_divider()
        self._draw_status_card()
        self._update_colors()

    def _on_game_state_event(self, event: str, state: GameState):
        self._update_status_display()
