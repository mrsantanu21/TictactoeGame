"""
Settings Screen (Screen 6).
Light/Dark theme toggle with animated selection buttons,
and Sound ON/OFF toggle switch.
"""

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from services.sound_manager import sound_manager
from services.dp_utils import dp, scaled_h
from components.rounded_button import RoundedButton, IconButton, CanvasIcon
from game.game_state import GameState


class ToggleSwitchWidget(Widget):
    """
    Animated sliding ON/OFF toggle switch.
    Mimics a modern iOS/Android toggle.
    """

    def __init__(self, value: bool = True, on_toggle=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.on_toggle = on_toggle
        self.size_hint = (None, None)
        # Use dp() so the toggle switch is always finger-friendly on any DPI
        self.size = (dp(56), dp(30))
        self._knob_x_offset = 0.0
        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        t = theme_manager
        w, h = self.width, self.height
        with self.canvas:
            # Track background
            if self.value:
                Color(*t.get("PRIMARY"))
            else:
                Color(*t.get("BORDER"))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[h / 2])

            # Knob
            knob_r = (h - 6) / 2
            if self.value:
                knob_cx = self.right - knob_r - 3
            else:
                knob_cx = self.x + knob_r + 3
            Color(1, 1, 1, 1)
            Ellipse(
                pos=(knob_cx - knob_r, self.center_y - knob_r),
                size=(knob_r * 2, knob_r * 2),
            )

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.value = not self.value
            self._redraw()
            if self.on_toggle:
                self.on_toggle(self.value)
            return True
        return super().on_touch_down(touch)

    def _on_theme(self, tm):
        self._redraw()


class ThemeButton(Widget):
    """Single theme selection button: Light or Dark."""

    def __init__(self, label_text: str, icon: str, theme_name: str, is_active: bool = False, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self.label_text = label_text
        self.icon = icon
        self.theme_name = theme_name
        self.is_active = is_active
        self.on_tap = on_tap

        # Horizontal inner layout: icon + label
        from kivy.uix.boxlayout import BoxLayout as _BL
        self._inner = _BL(orientation="horizontal", spacing=6)
        self._inner.size_hint = (None, None)

        self.icon_widget = CanvasIcon(icon=icon, size_dp=20)
        self._inner.add_widget(self.icon_widget)

        self.lbl = Label(
            text=label_text,
            font_size="15sp",
            bold=True,
            size_hint=(None, 1),
        )
        self.lbl.texture_update()
        self._inner.add_widget(self.lbl)

        self.add_widget(self._inner)
        self.bind(pos=self._update, size=self._update)
        theme_manager.add_listener(self._on_theme)
        self._update()

    def set_active(self, active: bool):
        self.is_active = active
        self._update()

    def _update(self, *args):
        # Size the inner layout and center it
        self.lbl.texture_update()
        lbl_w = (self.lbl.texture_size[0] if self.lbl.texture else 60) + 4
        inner_w = 20 + 6 + lbl_w
        self._inner.size = (inner_w, 24)
        self._inner.center = self.center
        self._redraw()

    def _redraw(self):
        self.canvas.before.clear()
        t = theme_manager
        with self.canvas.before:
            if self.is_active:
                Color(*t.get("PRIMARY"))
            else:
                Color(*t.get("SURFACE"))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            if not self.is_active:
                Color(*t.get("BORDER"))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 16), width=1.1)

        fg = [1, 1, 1, 1] if self.is_active else t.get("PRIMARY_TEXT")
        self.lbl.color = fg
        self.icon_widget.set_color(fg)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.on_tap:
                self.on_tap(self.theme_name)
            return True
        return super().on_touch_down(touch)

    def _on_theme(self, tm):
        self._redraw()


class SoundRow(BoxLayout):
    """Horizontal row with speaker icon, 'Sound' label, and toggle switch."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = scaled_h(60)
        self.padding = [dp(16), dp(10), dp(16), dp(10)]
        self.spacing = dp(12)
        self.bind(pos=self._draw_bg, size=self._draw_bg)

        self.icon_widget = CanvasIcon(
            icon="speaker" if sound_manager.sound_enabled else "speaker_off",
            size_dp=30,
        )
        self.add_widget(self.icon_widget)

        self.label = Label(
            text="Sound",
            font_size="16sp",
            halign="left",
            valign="middle",
        )
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

        self.toggle = ToggleSwitchWidget(
            value=sound_manager.sound_enabled,
            on_toggle=self._on_toggle,
        )
        self.add_widget(self.toggle)

        theme_manager.add_listener(self._on_theme)
        self._on_theme(theme_manager)

    def _draw_bg(self, *args):
        self.canvas.before.clear()
        t = theme_manager
        with self.canvas.before:
            Color(*t.get("SURFACE"))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            Color(*t.get("BORDER"))
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 16), width=1.1)

    def _on_toggle(self, value: bool):
        sound_manager.set_enabled(value)
        self.icon_widget.icon_type = "speaker" if value else "speaker_off"
        self.icon_widget._redraw()

    def _on_theme(self, tm):
        t = tm
        self.label.color = t.get("PRIMARY_TEXT")
        self.icon_widget.set_color(t.get("PRIMARY_TEXT"))
        self._draw_bg()


class SettingsScreen(Screen):
    """Screen 6: Settings Screen — Theme and Sound controls."""

    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self.bg_widget = Widget(size_hint=(1, 1))
        self.bg_widget.bind(pos=self._draw_bg, size=self._draw_bg)
        self.root_layout.add_widget(self.bg_widget)

        self.content = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(18), dp(24), dp(32)],
            spacing=dp(24),
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.content)

        # HEADER
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=scaled_h(52))
        self.btn_back = IconButton(icon="back", on_click=self._go_back)
        header.add_widget(self.btn_back)
        self.header_title = Label(
            text="Settings",
            font_size="20sp",
            bold=True,
            halign="center",
            valign="middle",
        )
        self.header_title.bind(size=self.header_title.setter("text_size"))
        header.add_widget(self.header_title)
        header.add_widget(Widget(size_hint=(None, 1), width=dp(44)))
        self.content.add_widget(header)

        self.content.add_widget(Widget(size_hint_y=0.03))

        # THEME SECTION
        self.theme_lbl = Label(
            text="Theme",
            font_size="17sp",
            bold=True,
            size_hint=(1, None),
            height=28,
            halign="left",
            valign="middle",
        )
        self.theme_lbl.bind(size=self.theme_lbl.setter("text_size"))
        self.content.add_widget(self.theme_lbl)

        # Two side-by-side theme buttons
        theme_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=scaled_h(56), spacing=dp(12))

        self.btn_light = ThemeButton(
            label_text="Light",
            icon="sun",
            theme_name="light",
            is_active=(theme_manager.current_theme == "light"),
            on_tap=self._set_theme,
        )
        theme_row.add_widget(self.btn_light)

        self.btn_dark = ThemeButton(
            label_text="Dark",
            icon="moon",
            theme_name="dark",
            is_active=(theme_manager.current_theme == "dark"),
            on_tap=self._set_theme,
        )
        theme_row.add_widget(self.btn_dark)

        self.content.add_widget(theme_row)

        # Spacer / divider
        self.divider = Widget(size_hint=(1, None), height=dp(1))
        self.divider.bind(pos=self._draw_divider, size=self._draw_divider)
        self.content.add_widget(self.divider)

        # SOUND SECTION
        self.sound_section_lbl = Label(
            text="Sound",
            font_size="17sp",
            bold=True,
            size_hint=(1, None),
            height=28,
            halign="left",
            valign="middle",
        )
        self.sound_section_lbl.bind(size=self.sound_section_lbl.setter("text_size"))
        self.content.add_widget(self.sound_section_lbl)

        self.sound_row = SoundRow()
        self.content.add_widget(self.sound_row)

        # SCORE quick-access
        self.content.add_widget(Widget(size_hint_y=1))
        self.btn_view_score = RoundedButton(
            text="View Scores",
            style="surface",
            height=52,
            font_size="16sp",
            on_click=self._go_score,
        )
        self.content.add_widget(self.btn_view_score)

        theme_manager.add_listener(self._on_theme)
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

    def _draw_divider(self, *args):
        self.divider.canvas.clear()
        t = theme_manager
        with self.divider.canvas:
            Color(*t.get("BORDER"))
            Line(
                points=[self.divider.x, self.divider.center_y, self.divider.right, self.divider.center_y],
                width=0.9,
            )

    def _set_theme(self, theme_name: str):
        theme_manager.set_theme(theme_name)
        self.btn_light.set_active(theme_name == "light")
        self.btn_dark.set_active(theme_name == "dark")

    def _update_colors(self):
        t = theme_manager
        self.header_title.color = t.get("PRIMARY_TEXT")
        self.theme_lbl.color = t.get("PRIMARY_TEXT")
        self.sound_section_lbl.color = t.get("PRIMARY_TEXT")
        self._draw_bg()
        self._draw_divider()

    def _on_theme(self, tm):
        self._update_colors()

    def _go_back(self):
        if self.manager:
            self.manager.transition.direction = "right"
            prev = self.manager.previous()
            self.manager.current = prev if prev else "home"

    def _go_score(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "score"
