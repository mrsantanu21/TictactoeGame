"""
Rounded Button and Icon Button components.
Responsive, touch-friendly, canvas-rendered buttons with theme awareness and tactile feedback.
"""

import math
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager


def _draw_vector_icon(canvas_ctx, icon: str, cx: float, cy: float, r: float):
    """
    Draw a vector icon into an open `with canvas_ctx:` block.
    Caller is responsible for setting the Color before calling.
    `r` is the available radius / half-size of the icon area.
    """
    if icon == "play":
        # Right-pointing triangle
        h = r * 0.85
        w = h * 0.88
        pts = [
            cx - w * 0.4, cy - h / 2,
            cx + w * 0.6, cy,
            cx - w * 0.4, cy + h / 2,
            cx - w * 0.4, cy - h / 2,
        ]
        Line(points=pts, width=1.6, cap="round", joint="round")

    elif icon == "sun":
        # Circle + 8 short rays
        cr = r * 0.38
        Line(circle=(cx, cy, cr), width=1.8)
        n_rays = 8
        for i in range(n_rays):
            a = math.radians(i * 360 / n_rays)
            x0 = cx + math.cos(a) * (cr + r * 0.14)
            y0 = cy + math.sin(a) * (cr + r * 0.14)
            x1 = cx + math.cos(a) * (cr + r * 0.36)
            y1 = cy + math.sin(a) * (cr + r * 0.36)
            Line(points=[x0, y0, x1, y1], width=1.5, cap="round")

    elif icon == "moon":
        # Crescent: outer arc + inner arc (approximated with polyline)
        outer_r = r * 0.75
        inner_r = r * 0.52
        offset_x = r * 0.22
        pts_outer = []
        pts_inner = []
        steps = 20
        start_a = math.radians(60)
        end_a = math.radians(300)
        for i in range(steps + 1):
            t = i / steps
            a = start_a + t * (end_a - start_a)
            pts_outer += [cx + math.cos(a) * outer_r, cy + math.sin(a) * outer_r]
        for i in range(steps + 1):
            t = i / steps
            a = end_a - t * (end_a - start_a)
            pts_inner += [cx + offset_x + math.cos(a) * inner_r, cy + math.sin(a) * inner_r]
        Line(points=pts_outer + pts_inner + pts_outer[:2], width=1.6, cap="round", joint="round")

    elif icon == "speaker":
        # Speaker cone + two arc waves
        bw = r * 0.30
        bh = r * 0.50
        # Speaker box
        Line(points=[
            cx - r * 0.50, cy - bh * 0.40,
            cx - r * 0.15, cy - bh * 0.40,
            cx + r * 0.22, cy - bh,
            cx + r * 0.22, cy + bh,
            cx - r * 0.15, cy + bh * 0.40,
            cx - r * 0.50, cy + bh * 0.40,
            cx - r * 0.50, cy - bh * 0.40,
        ], width=1.5, cap="round", joint="round")
        # Waves
        for scale in (0.55, 0.85):
            pts = []
            for i in range(9):
                t = i / 8
                a = math.radians(-70 + t * 140)
                pts += [cx + r * 0.30 + math.cos(a) * r * scale,
                        cy + math.sin(a) * r * scale]
            Line(points=pts, width=1.4, cap="round", joint="round")

    elif icon == "speaker_off":
        # Speaker (muted) — same cone, no waves, X mark
        bh = r * 0.50
        Line(points=[
            cx - r * 0.50, cy - bh * 0.40,
            cx - r * 0.15, cy - bh * 0.40,
            cx + r * 0.22, cy - bh,
            cx + r * 0.22, cy + bh,
            cx - r * 0.15, cy + bh * 0.40,
            cx - r * 0.50, cy + bh * 0.40,
            cx - r * 0.50, cy - bh * 0.40,
        ], width=1.5, cap="round", joint="round")
        d = r * 0.28
        mx = cx + r * 0.52
        Line(points=[mx - d, cy - d, mx + d, cy + d], width=1.8, cap="round")
        Line(points=[mx - d, cy + d, mx + d, cy - d], width=1.8, cap="round")

    elif icon == "people":
        # Two overlapping stick-figure heads + shoulders
        # Left person
        hr = r * 0.26
        Line(circle=(cx - r * 0.22, cy + r * 0.28, hr), width=1.7)
        Line(points=[
            cx - r * 0.22 - r * 0.30, cy - r * 0.20,
            cx - r * 0.22 - r * 0.30, cy + r * 0.08,
            cx - r * 0.22 + r * 0.30, cy + r * 0.08,
            cx - r * 0.22 + r * 0.30, cy - r * 0.20,
        ], width=1.7, cap="round", joint="round")
        # Right person (slightly overlapping)
        Line(circle=(cx + r * 0.22, cy + r * 0.28, hr), width=1.7)
        Line(points=[
            cx + r * 0.22 - r * 0.30, cy - r * 0.20,
            cx + r * 0.22 - r * 0.30, cy + r * 0.08,
            cx + r * 0.22 + r * 0.30, cy + r * 0.08,
            cx + r * 0.22 + r * 0.30, cy - r * 0.20,
        ], width=1.7, cap="round", joint="round")

    elif icon == "computer":
        # Monitor rectangle + stand + base
        mw = r * 1.10
        mh = r * 0.75
        mx = cx - mw / 2
        my = cy - r * 0.10
        Line(rounded_rectangle=(mx, my, mw, mh, 4), width=1.6)
        # Stand
        Line(points=[cx, my, cx, cy - r * 0.42], width=1.6, cap="round")
        # Base
        Line(points=[cx - r * 0.36, cy - r * 0.42, cx + r * 0.36, cy - r * 0.42],
             width=1.8, cap="round")

    elif icon == "trophy":
        # Trophy cup: bowl + handles + stem + base
        tw = r * 0.70
        # Bowl outline
        pts = []
        for i in range(13):
            t = i / 12
            a = math.radians(180 + t * 180)
            pts += [cx + math.cos(a) * tw / 2, cy + r * 0.45 + math.sin(a) * r * 0.46]
        Line(points=pts, width=1.7, cap="round", joint="round")
        # Left handle
        Line(points=[cx - tw / 2, cy + r * 0.45, cx - tw / 2 - r * 0.22, cy + r * 0.22,
                     cx - tw / 2, cy + r * 0.00], width=1.5, cap="round", joint="round")
        # Right handle
        Line(points=[cx + tw / 2, cy + r * 0.45, cx + tw / 2 + r * 0.22, cy + r * 0.22,
                     cx + tw / 2, cy + r * 0.00], width=1.5, cap="round", joint="round")
        # Stem
        Line(points=[cx, cy - r * 0.01, cx, cy - r * 0.42], width=1.7, cap="round")
        # Base
        Line(points=[cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy - r * 0.42],
             width=2.0, cap="round")

    elif icon == "check":
        # Checkmark
        Line(
            points=[cx - r * 0.50, cy, cx - r * 0.10, cy - r * 0.42, cx + r * 0.52, cy + r * 0.38],
            width=2.0, cap="round", joint="round",
        )

    elif icon in ("game", "gamepad", "joystick"):
        # Arcade joystick / controller icon (Screen 4 status card)
        bw = r * 0.55
        bh = r * 0.28
        by = cy - r * 0.38
        Line(rounded_rectangle=(cx - bw, by, bw * 2, bh, 3), width=1.6)
        # Joystick stem
        Line(points=[cx, by + bh, cx, cy + r * 0.15], width=2.2, cap="round")
        # Ball head
        Line(circle=(cx, cy + r * 0.30, r * 0.18), width=1.8)


class CanvasIcon(Widget):
    """
    A small fixed-size widget that draws a vector icon on its canvas.
    Use anywhere a unicode emoji Label would break (SDL2 / Android glyph issues).
    """

    def __init__(self, icon: str, size_dp: float = 24.0, color=None, **kwargs):
        super().__init__(**kwargs)
        self.icon_type = icon
        self.icon_color = color  # If None, uses theme PRIMARY_TEXT
        self.size_hint = (None, None)
        self.size = (size_dp, size_dp)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def set_color(self, color):
        self.icon_color = color
        self._redraw()

    def _redraw(self, *args):
        if self.width < 2:
            return
        self.canvas.clear()
        col = self.icon_color if self.icon_color else theme_manager.get("PRIMARY_TEXT")
        r = min(self.width, self.height) / 2.0 * 0.82
        with self.canvas:
            Color(*col)
            _draw_vector_icon(self.canvas, self.icon_type, self.center_x, self.center_y, r)


class RoundedButton(ButtonBehavior, BoxLayout):
    """
    A modern pill/rounded button with customizable style, icon, and label.
    Styles:
      - 'primary': deep forest green, white text
      - 'surface': light cream surface with subtle border, dark text
      - 'toggle_on': active selected style (primary color)
      - 'toggle_off': unselected style (surface with border)
      - 'disabled': dimmed card with coming soon indicator
    """

    def __init__(
        self,
        text: str = "",
        icon: str = "",
        style: str = "primary",
        radius: float = 24.0,
        height: float = 56.0,
        font_size: str = "17sp",
        bold: bool = True,
        on_click=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = height
        self.spacing = 10
        self.padding = [20, 8, 20, 8]

        self.btn_text = text
        self.btn_icon = icon
        self.btn_style = style
        self.radius = radius
        self.font_size = font_size
        self.is_bold = bold
        self.on_click = on_click
        self._is_pressed = False

        # Build inner widgets
        self.icon_label = None
        if self.btn_icon:
            self.icon_label = CanvasIcon(
                icon=self.btn_icon,
                size_dp=22,
            )
            self.add_widget(self.icon_label)

        self.text_label = Label(
            text=self.btn_text,
            font_size=self.font_size,
            bold=self.is_bold,
            halign="center",
            valign="middle",
        )
        self.text_label.bind(size=self.text_label.setter("text_size"))
        self.add_widget(self.text_label)

        # Right accessory (e.g. chevron or badge)
        self.right_accessory = None

        # Bind graphics and theme
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        theme_manager.add_listener(self._on_theme_changed)
        self._update_canvas()

    def _map_icon_symbol(self, icon: str) -> str:
        # Kept for backwards compat — not used for rendering anymore
        return icon

    def set_right_accessory(self, widget: Widget) -> None:
        if self.right_accessory and self.right_accessory in self.children:
            self.remove_widget(self.right_accessory)
        self.right_accessory = widget
        if widget:
            self.add_widget(widget)

    def set_text(self, text: str) -> None:
        self.btn_text = text
        self.text_label.text = text

    def set_style(self, style: str) -> None:
        self.btn_style = style
        self._update_canvas()

    def _get_colors(self):
        t = theme_manager
        if self.btn_style in ("primary", "toggle_on"):
            bg = t.get("PRIMARY")
            fg = [1, 1, 1, 1] if not t.is_dark else [0.12, 0.14, 0.12, 1]
            border = None
        elif self.btn_style == "surface" or self.btn_style == "toggle_off":
            bg = t.get("SURFACE")
            fg = t.get("PRIMARY_TEXT")
            border = t.get("BORDER")
        elif self.btn_style == "disabled":
            bg = t.get("SURFACE")
            fg = t.get("SECONDARY_TEXT")
            border = t.get("BORDER")
        elif self.btn_style == "status":
            bg = t.get("PRIMARY_LIGHT")
            fg = t.get("PRIMARY_TEXT")
            border = None
        else:
            bg = t.get("PRIMARY")
            fg = [1, 1, 1, 1]
            border = None

        if self._is_pressed and self.btn_style != "disabled":
            # Slightly darken/shift on touch
            bg = [max(0.0, c * 0.88) for c in bg[:3]] + [bg[3]]

        return bg, fg, border

    def _update_canvas(self, *args) -> None:
        self.canvas.before.clear()
        bg_color, fg_color, border_color = self._get_colors()

        with self.canvas.before:
            # Background fill
            Color(*bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius],
            )
            # Optional border
            if border_color:
                Color(*border_color)
                Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius),
                    width=1.2,
                )

        if self.text_label:
            self.text_label.color = fg_color
        if self.icon_label:
            self.icon_label.set_color(fg_color)

    def on_press(self):
        if self.btn_style == "disabled":
            return
        self._is_pressed = True
        self._update_canvas()

    def on_release(self):
        self._is_pressed = False
        self._update_canvas()
        if self.btn_style != "disabled" and self.on_click:
            self.on_click()

    def _on_theme_changed(self, tm):
        self._update_canvas()


class IconButton(ButtonBehavior, Widget):
    """
    A compact touch-friendly icon button for headers and toolbars.
    All icons are drawn entirely with Kivy canvas primitives (no unicode glyphs),
    so they render correctly on all platforms including Windows SDL2 and Android.

    Supported icons: 'back', 'gear', 'menu', 'close'
    """

    def __init__(
        self,
        icon: str = "menu",
        size_dp: float = 44.0,
        on_click=None,
        **kwargs,
    ):
        # Drop icon_size kwarg silently if passed from old call sites
        kwargs.pop("icon_size", None)
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (size_dp, size_dp)
        self.icon_type = icon
        self.on_click = on_click
        self._is_pressed = False

        self.bind(pos=self._redraw, size=self._redraw)
        theme_manager.add_listener(self._on_theme_changed)
        self._redraw()

    def set_icon(self, icon: str) -> None:
        self.icon_type = icon
        self._redraw()

    # ------------------------------------------------------------------
    # Canvas rendering
    # ------------------------------------------------------------------

    def _redraw(self, *args):
        """Redraw chip background + vector icon entirely on canvas."""
        import math

        if self.width < 2 or self.height < 2:
            return

        self.canvas.clear()
        t = theme_manager

        cx, cy = self.center_x, self.center_y

        # Chip geometry — inset 4 dp from the touch area
        inset = 4
        chip_r = (min(self.width, self.height) - inset * 2) / 2.0

        # Colors
        icon_col = t.get("PRIMARY") if self._is_pressed else t.get("PRIMARY_TEXT")

        with self.canvas:
            # Subtle touch feedback highlight on press
            if self._is_pressed:
                Color(*t.get("PRIMARY_LIGHT"))
                Ellipse(
                    pos=(cx - chip_r, cy - chip_r),
                    size=(chip_r * 2, chip_r * 2),
                )

            # ── Vector icon ───────────────────────────────────────────
            Color(*icon_col)

            if self.icon_type == "back":
                # Clean minimal left-pointing chevron  ‹
                arm = chip_r * 0.32          # half-height
                tip_x = cx - chip_r * 0.14  # x of the V tip
                stem_x = cx + chip_r * 0.16  # x of the open ends
                Line(
                    points=[stem_x, cy + arm, tip_x, cy, stem_x, cy - arm],
                    width=2.2,
                    cap="round",
                    joint="round",
                )

            elif self.icon_type == "gear":
                # Settings gear: minimal 6-tooth gear
                n = 6
                inner_r = chip_r * 0.20
                outer_r = chip_r * 0.50
                tooth_w = 2.4

                # Center hole
                Line(circle=(cx, cy, inner_r), width=1.8)

                # Teeth
                for i in range(n):
                    angle = math.radians(i * 360.0 / n)
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    x0 = cx + cos_a * (inner_r + 1.5)
                    y0 = cy + sin_a * (inner_r + 1.5)
                    x1 = cx + cos_a * outer_r
                    y1 = cy + sin_a * outer_r
                    Line(points=[x0, y0, x1, y1], width=tooth_w, cap="round")

                # Body ring
                Line(circle=(cx, cy, (inner_r + outer_r) / 2.0), width=1.6)

            elif self.icon_type == "menu":
                # Hamburger — three clean horizontal bars
                bar_w = chip_r * 0.44
                gap = chip_r * 0.28
                for dy in (gap, 0, -gap):
                    Line(
                        points=[cx - bar_w, cy + dy, cx + bar_w, cy + dy],
                        width=2.0,
                        cap="round",
                    )

            elif self.icon_type == "close":
                # X cross
                d = chip_r * 0.38
                Line(points=[cx - d, cy - d, cx + d, cy + d], width=2.0, cap="round")
                Line(points=[cx - d, cy + d, cx + d, cy - d], width=2.0, cap="round")

    # ------------------------------------------------------------------
    # Touch / theme
    # ------------------------------------------------------------------

    def on_press(self):
        self._is_pressed = True
        self._redraw()

    def on_release(self):
        self._is_pressed = False
        self._redraw()
        if self.on_click:
            self.on_click()

    def _on_theme_changed(self, tm):
        self._redraw()
