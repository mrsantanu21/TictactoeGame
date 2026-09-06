"""
Tic-Tac-Toe — Minimalist Android 17-Inspired Edition
Python + Tkinter only. No external dependencies.

Run:
    python tic_tac_toe.py
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# ----------------------------------------------------------------------------
# COLOR TOKENS
# ----------------------------------------------------------------------------
LIGHT = {
    "BG": "#E5DDD0",
    "SURFACE": "#FBF3E8",
    "SURFACE_ALT": "#F7EFE4",
    "PRIMARY": "#6A866A",
    "PRIMARY_DARK": "#5F7A5F",
    "SECONDARY": "#A67B5B",
    "TERTIARY": "#F5F5DC",
    "NEUTRAL": "#364136",
    "TEXT_SECONDARY": "#746F66",
    "X_COLOR": "#364136",
    "O_COLOR": "#6A866A",
    "WIN_COLOR": "#A67B5B",
    "HOVER_BG": "#EEE4D7",
    "DIVIDER": "#DED5C8",
    "STATUS_BG": "#E2E9D8",
    "ON_PRIMARY": "#FFFFFF",
}

DARK = {
    "BG": "#2A2620",
    "SURFACE": "#39332B",
    "SURFACE_ALT": "#423B31",
    "PRIMARY": "#7FA37F",
    "PRIMARY_DARK": "#5D8060",
    "SECONDARY": "#C79A72",
    "TERTIARY": "#4A4536",
    "NEUTRAL": "#F0E8DC",
    "TEXT_SECONDARY": "#B8AFA2",
    "X_COLOR": "#F0E8DC",
    "O_COLOR": "#7FA37F",
    "WIN_COLOR": "#C79A72",
    "HOVER_BG": "#453E34",
    "DIVIDER": "#544C40",
    "STATUS_BG": "#3D4A3D",
    "ON_PRIMARY": "#1F1B16",
}

WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

DEMO_BOARD = ["X", "O", "X", "O", "X", "", "O", "", "X"]  # decorative only


# ----------------------------------------------------------------------------
# FONT HELPERS
# ----------------------------------------------------------------------------
def pick_font(root, candidates, size, weight="normal"):
    try:
        available = set(tkfont.families(root))
    except Exception:
        available = set()
    for fam in candidates:
        if fam in available:
            return (fam, size, weight)
    return ("Arial", size, weight)


# ----------------------------------------------------------------------------
# DRAWING HELPERS
# ----------------------------------------------------------------------------
def rounded_rect_points(x1, y1, x2, y2, r):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]


def draw_rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    if x2 - x1 < 2 or y2 - y1 < 2:
        return None
    pts = rounded_rect_points(x1, y1, x2, y2, r)
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ----------------------------------------------------------------------------
# REUSABLE WIDGETS
# ----------------------------------------------------------------------------
class Card(tk.Frame):
    """A cream rounded-corner surface. Put child widgets inside `.inner`."""

    def __init__(self, parent, theme, radius=22, bg_key="SURFACE",
                 padx=22, pady=20, **kw):
        tk.Frame.__init__(self, parent, bg=theme["BG"], **kw)
        self.theme = theme
        self.bg_key = bg_key
        self.radius = radius
        self.pad = (padx, pady)

        self.canvas = tk.Canvas(self, width=1, height=1, bg=theme["BG"],
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=theme[bg_key])
        self.win_id = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        w, h = event.width, event.height
        self.canvas.delete("cardbg")
        draw_rounded_rect(self.canvas, 1, 1, max(w - 1, 3), max(h - 1, 3),
                           self.radius, fill=self.theme[self.bg_key],
                           outline="", tags="cardbg")
        self.canvas.tag_lower("cardbg")
        px, py = self.pad
        self.canvas.coords(self.win_id, px, py)
        self.canvas.itemconfig(self.win_id,
                                width=max(w - 2 * px, 1),
                                height=max(h - 2 * py, 1))


class RoundedButton(tk.Canvas):
    """Canvas-based rounded button (never uses default Tk button chrome)."""

    def __init__(self, parent, theme, text, command=None, icon="",
                 style="primary", font=None, radius=14,
                 width=170, height=44):
        tk.Canvas.__init__(self, parent, width=width, height=height,
                            bg=theme["SURFACE"], highlightthickness=0,
                            cursor="hand2")
        self.theme = theme
        self.text = text
        self.icon = icon
        self.command = command
        self.style = style  # "primary" | "outline" | "flat" | "toggle_on" | "toggle_off"
        self.radius = radius
        self.font = font or ("Arial", 11, "bold")
        self._hover = False
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)
        self.after(10, self.redraw)

    def set_style(self, style):
        self.style = style
        self.redraw()

    def set_text(self, text):
        self.text = text
        self.redraw()

    def redraw(self):
        self.delete("all")
        w = self.winfo_width() or int(self["width"])
        h = self.winfo_height() or int(self["height"])
        t = self.theme

        if self.style == "primary":
            fill = t["PRIMARY_DARK"] if self._hover else t["PRIMARY"]
            fg = t["ON_PRIMARY"]
            outline = ""
        elif self.style == "toggle_on":
            fill = t["PRIMARY_DARK"] if self._hover else t["PRIMARY"]
            fg = t["ON_PRIMARY"]
            outline = ""
        else:  # outline / toggle_off / flat (unselected)
            fill = t["HOVER_BG"] if self._hover else t["SURFACE"]
            fg = t["NEUTRAL"]
            outline = t["DIVIDER"]

        draw_rounded_rect(self, 1, 1, max(w - 1, 3), max(h - 1, 3),
                           self.radius, fill=fill, outline=outline, width=1)
        if self.icon in {"people", "robot", "play"}:
            icon_size = 20
            gap = 12
            text_w = tkfont.Font(font=self.font).measure(self.text)
            total_w = icon_size + gap + text_w
            start_x = (w - total_w) / 2
            icon_cx = start_x + icon_size / 2
            if self.icon == "people":
                draw_icon_people(self, icon_cx, h / 2, icon_size, fg)
            elif self.icon == "robot":
                draw_icon_robot(self, icon_cx, h / 2, icon_size, fg)
            else:
                draw_icon_play(self, icon_cx, h / 2, icon_size, fg)
            self.create_text(start_x + icon_size + gap + text_w / 2, h / 2,
                             text=self.text, fill=fg, font=self.font)
        else:
            label = (self.icon + "  " if self.icon else "") + self.text
            self.create_text(w / 2, h / 2, text=label, fill=fg, font=self.font)
        self.configure(bg=t["SURFACE"])

    def _enter(self, e):
        self._hover = True
        self.redraw()

    def _leave(self, e):
        self._hover = False
        self.redraw()

    def _click(self, e):
        if self.command:
            self.command()


class ToggleSwitch(tk.Canvas):
    """A small sliding on/off switch, e.g. for Sound."""

    def __init__(self, parent, theme, value=True, command=None,
                 width=48, height=26):
        tk.Canvas.__init__(self, parent, width=width, height=height,
                            bg=theme["SURFACE"], highlightthickness=0,
                            cursor="hand2")
        self.theme = theme
        self.value = value
        self.command = command
        self.bind("<Button-1>", self.toggle)
        self.after(10, self.redraw)
        self.bind("<Configure>", lambda e: self.redraw())

    def toggle(self, event=None):
        self.value = not self.value
        self.redraw()
        if self.command:
            self.command(self.value)

    def redraw(self):
        self.delete("all")
        w = self.winfo_width() or int(self["width"])
        h = self.winfo_height() or int(self["height"])
        t = self.theme
        fill = t["PRIMARY"] if self.value else t["DIVIDER"]
        draw_rounded_rect(self, 0, 0, w, h, h / 2, fill=fill, outline="")
        r = h / 2 - 3
        knob_x = w - h / 2 if self.value else h / 2
        self.create_oval(knob_x - r, h / 2 - r, knob_x + r, h / 2 + r,
                          fill="#FFFFFF", outline="")
        self.configure(bg=t["SURFACE"])


def draw_icon_menu(canvas, cx, cy, size, color):
    """Simple hamburger icon."""
    half = size / 2
    for i in range(3):
        y = cy - half + i * half
        canvas.create_line(cx - half, y, cx + half, y, fill=color,
                            width=2, capstyle="round")


def draw_icon_gear(canvas, cx, cy, r, color):
    """Simple gear/settings icon (outer circle + tick marks + inner circle)."""
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=2)
    canvas.create_oval(cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35,
                        outline=color, width=2)
    import math
    for i in range(8):
        ang = i * (math.pi / 4)
        x1 = cx + math.cos(ang) * r * 1.15
        y1 = cy + math.sin(ang) * r * 1.15
        x2 = cx + math.cos(ang) * r * 1.4
        y2 = cy + math.sin(ang) * r * 1.4
        canvas.create_line(x1, y1, x2, y2, fill=color, width=2, capstyle="round")


def draw_icon_people(canvas, cx, cy, size, color):
    """Two small user silhouettes for the Player vs Player button."""
    r = size * 0.17
    canvas.create_oval(cx - 8 - r, cy - 8 - r, cx - 8 + r, cy - 8 + r,
                       outline=color, width=2)
    canvas.create_oval(cx + 4 - r, cy - 6 - r, cx + 4 + r, cy - 6 + r,
                       outline=color, width=2)
    canvas.create_arc(cx - 17, cy - 2, cx + 2, cy + 16, start=20, extent=140,
                      outline=color, width=2, style="arc")
    canvas.create_arc(cx - 5, cy - 1, cx + 15, cy + 16, start=20, extent=140,
                      outline=color, width=2, style="arc")


def draw_icon_robot(canvas, cx, cy, size, color):
    """Small rounded robot face for the Player vs AI button."""
    w = size * 0.78
    h = size * 0.68
    draw_rounded_rect(canvas, cx - w / 2, cy - h / 2 + 2,
                      cx + w / 2, cy + h / 2 + 2, 5,
                      fill="", outline=color, width=2)
    canvas.create_line(cx, cy - h / 2 + 2, cx, cy - h / 2 - 5,
                       fill=color, width=2, capstyle="round")
    canvas.create_oval(cx - 2, cy - h / 2 - 9, cx + 2, cy - h / 2 - 5,
                       fill=color, outline=color)
    canvas.create_oval(cx - 5, cy, cx - 2, cy + 3, fill=color, outline=color)
    canvas.create_oval(cx + 2, cy, cx + 5, cy + 3, fill=color, outline=color)
    canvas.create_line(cx - 4, cy + 8, cx + 4, cy + 8,
                       fill=color, width=2, capstyle="round")


def draw_icon_play(canvas, cx, cy, size, color):
    """Outlined play triangle for the New Game button."""
    pts = [cx - size * 0.26, cy - size * 0.36,
           cx - size * 0.26, cy + size * 0.36,
           cx + size * 0.34, cy]
    canvas.create_polygon(pts, outline=color, fill="", width=2)


def draw_icon_trophy(canvas, cx, cy, size, color):
    """Line trophy icon used in the status pill."""
    cup_w = size * 0.55
    cup_h = size * 0.45
    top = cy - size * 0.35
    canvas.create_rectangle(cx - cup_w / 2, top, cx + cup_w / 2, top + cup_h,
                            outline=color, width=2)
    canvas.create_arc(cx - cup_w / 2 - 9, top + 2, cx - cup_w / 2 + 8,
                      top + cup_h + 8, start=270, extent=-170,
                      outline=color, width=2, style="arc")
    canvas.create_arc(cx + cup_w / 2 - 8, top + 2, cx + cup_w / 2 + 9,
                      top + cup_h + 8, start=270, extent=170,
                      outline=color, width=2, style="arc")
    canvas.create_line(cx, top + cup_h, cx, cy + size * 0.28,
                       fill=color, width=2, capstyle="round")
    canvas.create_line(cx - size * 0.22, cy + size * 0.28,
                       cx + size * 0.22, cy + size * 0.28,
                       fill=color, width=2, capstyle="round")
    canvas.create_line(cx - size * 0.32, cy + size * 0.39,
                       cx + size * 0.32, cy + size * 0.39,
                       fill=color, width=2, capstyle="round")


# ----------------------------------------------------------------------------
# MAIN APPLICATION
# ----------------------------------------------------------------------------
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("1600x950")
        self.root.minsize(1300, 780)

        # ---- state ----
        self.theme_name = "light"
        self.theme = LIGHT
        self.sound_on = True
        self.board = [""] * 9
        self.current_player = "X"
        self.scores = {"X": 0, "O": 0}
        self.winning_line = None
        self.game_over = False
        self._hover_cell = None
        self._board_geom = None

        # ---- fonts ----
        self.font_heading = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 22, "bold")
        self.font_brand = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 17, "bold")
        self.font_card_title = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 16, "bold")
        self.font_body = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 12)
        self.font_body_bold = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 12, "bold")
        self.font_small = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 10)
        self.font_mark = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 14, "bold")
        self.font_btn = pick_font(root, ["Manrope", "Segoe UI", "Arial"], 12, "bold")

        self._build_ui()
        self._update_ui()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def _build_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        t = self.theme
        self.root.configure(bg=t["BG"])

        # Style the PanedWindow sash to match the theme (thin, themed divider)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Resizable.TPanedwindow",
                        background=t["BG"],
                        sashwidth=8,
                        sashpad=2)
        style.configure("Resizable.Sash",
                        sashthickness=8,
                        background=t["DIVIDER"],
                        relief="flat")

        # Outer paned window — three horizontally draggable panes
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                style="Resizable.TPanedwindow")
        paned.pack(fill="both", expand=True, padx=28, pady=36)

        # ---------------- LEFT PANE ----------------
        left = tk.Frame(paned, bg=t["BG"])
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=2)
        left.grid_rowconfigure(1, weight=1)
        paned.add(left, weight=7)

        intro_card = Card(left, t, radius=24, padx=20, pady=20)
        intro_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 16))
        self._build_intro_card(intro_card.inner)

        score_card = Card(left, t, radius=24, padx=20, pady=20)
        score_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self._build_score_card(score_card.inner)

        # ---------------- MIDDLE PANE ----------------
        mid = tk.Frame(paned, bg=t["BG"])
        mid.grid_columnconfigure(0, weight=1)
        mid.grid_rowconfigure(0, weight=0)   # Game Mode
        mid.grid_rowconfigure(1, weight=4)   # Board
        mid.grid_rowconfigure(2, weight=0)   # New Game
        paned.add(mid, weight=10)

        mode_card = Card(mid, t, radius=24, padx=30, pady=26)
        mode_card.configure(height=168)
        mode_card.pack_propagate(False)
        mode_card.grid(row=0, column=0, sticky="ew", padx=8, pady=(0, 16))
        self._build_mode_card(mode_card.inner)

        board_card = Card(mid, t, radius=24, padx=20, pady=26)
        board_card.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 16))
        self._build_board_card(board_card.inner)

        newgame_card = Card(mid, t, radius=24, padx=20, pady=20)
        newgame_card.configure(height=102)
        newgame_card.pack_propagate(False)
        newgame_card.grid(row=2, column=0, sticky="ew", padx=8)
        self._build_newgame_card(newgame_card.inner)

        # ---------------- RIGHT PANE ----------------
        right = tk.Frame(paned, bg=t["BG"])
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=33)
        right.grid_rowconfigure(1, weight=23)
        right.grid_rowconfigure(2, weight=37)
        paned.add(right, weight=7)

        players_card = Card(right, t, radius=24, padx=20, pady=20)
        players_card.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(0, 16))
        self._build_players_card(players_card.inner)

        status_card = Card(right, t, radius=24, padx=20, pady=18)
        status_card.grid(row=1, column=0, sticky="nsew", padx=(8, 0), pady=(0, 16))
        self._build_status_card(status_card.inner)

        settings_card = Card(right, t, radius=24, padx=20, pady=20)
        settings_card.grid(row=2, column=0, sticky="nsew", padx=(8, 0))
        self._build_settings_card(settings_card.inner)

    # ---- Intro / sample-board card (decorative, left-top) ----
    def _build_intro_card(self, parent):
        t = self.theme
        # Header row: hamburger | centered title | spacer
        header = tk.Frame(parent, bg=t["SURFACE"])
        header.pack(fill="x")
        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        menu_canvas = tk.Canvas(header, width=28, height=28, bg=t["SURFACE"],
                                 highlightthickness=0)
        menu_canvas.grid(row=0, column=0, sticky="w")
        draw_icon_menu(menu_canvas, 14, 14, 14, t["NEUTRAL"])

        tk.Label(header, text="Tic Tac Toe", font=self.font_brand,
                 bg=t["SURFACE"], fg="#0F1210").grid(row=0, column=1)
        tk.Frame(header, width=28, height=28, bg=t["SURFACE"]).grid(
            row=0, column=2, sticky="e")

        # Decorative board – fills expanding space between header and tagline
        demo = tk.Canvas(parent, bg=t["SURFACE"], highlightthickness=0)
        demo.pack(fill="both", expand=True, pady=(14, 8))

        def draw_demo(event=None):
            demo.delete("all")
            w = demo.winfo_width() or 240
            h = demo.winfo_height() or 200
            # Keep board square and centered, with generous margin
            size = min(w, h) - 18
            if size < 10:
                return
            x0 = (w - size) / 2
            y0 = (h - size) / 2
            cell = size / 3
            # Grid lines – match image: NEUTRAL color (dark brown), width 2
            for i in (1, 2):
                demo.create_line(x0 + i * cell, y0 + 6,
                                  x0 + i * cell, y0 + size - 6,
                                  fill=t["NEUTRAL"], width=4, capstyle="round")
                demo.create_line(x0 + 6, y0 + i * cell,
                                  x0 + size - 6, y0 + i * cell,
                                  fill=t["NEUTRAL"], width=4, capstyle="round")
            # Marks: X=dark, O=green
            for idx, val in enumerate(DEMO_BOARD):
                if not val:
                    continue
                r, c = divmod(idx, 3)
                cx = x0 + c * cell + cell / 2
                cy = y0 + r * cell + cell / 2
                pad = cell * 0.28
                if val == "X":
                    demo.create_line(cx - pad, cy - pad, cx + pad, cy + pad,
                                      fill=t["X_COLOR"], width=7, capstyle="round")
                    demo.create_line(cx - pad, cy + pad, cx + pad, cy - pad,
                                      fill=t["X_COLOR"], width=7, capstyle="round")
                else:
                    demo.create_oval(cx - pad, cy - pad, cx + pad, cy + pad,
                                      outline=t["O_COLOR"], width=7)

        demo.bind("<Configure>", draw_demo)

        tk.Label(parent, text="Think  •  Match  •  Win", font=self.font_small,
                 bg=t["SURFACE"], fg=t["TEXT_SECONDARY"]).pack(pady=(2, 0))

    # ---- Score card ----
    def _build_score_card(self, parent):
        t = self.theme
        tk.Label(parent, text="Score", font=self.font_card_title,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(anchor="w", pady=(0, 14))

        self.score_labels = {}
        for idx, (mark, color) in enumerate((("X", t["X_COLOR"]), ("O", t["O_COLOR"]))):
            row = tk.Frame(parent, bg=t["SURFACE"])
            row.pack(fill="x", pady=6)

            avatar = tk.Canvas(row, width=42, height=42, bg=t["SURFACE"],
                                highlightthickness=0)
            avatar.pack(side="left")
            avatar.create_oval(1, 1, 41, 41, fill=color, outline="")
            self._draw_mark(avatar, 21, 21, 10, mark, t["SURFACE"])

            tk.Label(row, text=f"Player {mark}", font=self.font_body,
                     bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(side="left", padx=12)

            score_lbl = tk.Label(row, text="0", font=self.font_body_bold,
                                  bg=t["SURFACE"], fg=t["NEUTRAL"])
            score_lbl.pack(side="right")
            self.score_labels[mark] = score_lbl

            if idx == 0:
                tk.Frame(parent, bg=t["DIVIDER"], height=1).pack(fill="x", pady=(8, 8))

    def _draw_mark(self, canvas, cx, cy, pad, mark, bg):
        if mark == "X":
            canvas.create_line(cx - pad, cy - pad, cx + pad, cy + pad,
                                fill=bg, width=3, capstyle="round")
            canvas.create_line(cx - pad, cy + pad, cx + pad, cy - pad,
                                fill=bg, width=3, capstyle="round")
        else:
            canvas.create_oval(cx - pad, cy - pad, cx + pad, cy + pad,
                                outline=bg, width=3)

    # ---- Game Mode card ----
    def _build_mode_card(self, parent):
        t = self.theme
        header = tk.Frame(parent, bg=t["SURFACE"])
        header.pack(fill="x", pady=(0, 26))
        tk.Label(header, text="Game Mode", font=self.font_card_title,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(side="left")
        gear = tk.Canvas(header, width=24, height=24, bg=t["SURFACE"], highlightthickness=0)
        gear.pack(side="right")
        draw_icon_gear(gear, 12, 12, 6, t["NEUTRAL"])

        # Full-width Player vs Player button (only mode)
        self.btn_pvp = RoundedButton(
            parent, t, "Player vs Player", icon="people",
            style="toggle_on",
            font=self.font_btn, width=440, height=62)
        self.btn_pvp.pack(fill="x")

    # ---- Board card ----
    def _build_board_card(self, parent):
        t = self.theme
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        tk.Label(parent, text="Tic Tac Toe", font=self.font_heading,
                 bg=t["SURFACE"], fg="#0F1210").grid(
                     row=0, column=0, pady=(0, 28))

        board_frame = tk.Frame(parent, bg=t["SURFACE"])
        board_frame.grid(row=1, column=0, sticky="nsew")
        board_frame.grid_rowconfigure(0, weight=1)
        board_frame.grid_columnconfigure(0, weight=1)

        self.board_canvas = tk.Canvas(board_frame, bg=t["SURFACE"],
                                       highlightthickness=0)
        self.board_canvas.grid(row=0, column=0, sticky="nsew")
        self.board_canvas.bind("<Configure>", self._on_board_frame_resize)
        self.board_canvas.bind("<Button-1>", self._on_board_click)
        self.board_canvas.bind("<Motion>", self._on_board_hover)
        self.board_canvas.bind("<Leave>", lambda e: self._on_board_hover(None))
        board_frame.bind("<Configure>", self._on_board_frame_resize)

    def _on_board_frame_resize(self, event=None):
        if not hasattr(self, "board_canvas"):
            return
        self._draw_board()

    def _draw_board(self):
        c = self.board_canvas
        # Flush pending geometry so winfo_width/height reflect actual layout
        c.update_idletasks()
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 20 or h < 20:
            return
        t = self.theme
        padding = 34
        size = min(w, h) - padding * 2
        if size < 100:
            return
        x0 = (w - size) / 2
        y0 = (h - size) / 2
        self._board_geom = (x0, y0, size)
        cell = size / 3
        mark_pad = cell * 0.28   # scales with cell so marks fill the cell
        line_w = max(10, int(cell * 0.10))
        mark_w = max(12, int(cell * 0.18))  # scale mark stroke with cell size

        # hover highlight
        if (self._hover_cell is not None and not self.game_over
                and self.board[self._hover_cell] == ""):
            r, cc = divmod(self._hover_cell, 3)
            hx0, hy0 = x0 + cc * cell + 6, y0 + r * cell + 6
            draw_rounded_rect(c, hx0, hy0, hx0 + cell - 12, hy0 + cell - 12,
                               12, fill=t["HOVER_BG"], outline="")

        # grid lines – sage green, thick, full length
        for i in (1, 2):
            c.create_line(x0 + i * cell, y0, x0 + i * cell, y0 + size,
                           fill=t["PRIMARY"], width=line_w, capstyle="round")
            c.create_line(x0, y0 + i * cell, x0 + size, y0 + i * cell,
                           fill=t["PRIMARY"], width=line_w, capstyle="round")

        # marks – scaled to cell size
        for idx, val in enumerate(self.board):
            if val == "":
                continue
            r, cc = divmod(idx, 3)
            cx = x0 + cc * cell + cell / 2
            cy = y0 + r * cell + cell / 2
            is_win = self.winning_line is not None and idx in self.winning_line
            if val == "X":
                color = t["WIN_COLOR"] if is_win else t["X_COLOR"]
                c.create_line(cx - mark_pad, cy - mark_pad,
                              cx + mark_pad, cy + mark_pad,
                              fill=color, width=mark_w, capstyle="round")
                c.create_line(cx - mark_pad, cy + mark_pad,
                              cx + mark_pad, cy - mark_pad,
                              fill=color, width=mark_w, capstyle="round")
            else:
                color = t["WIN_COLOR"] if is_win else t["O_COLOR"]
                c.create_oval(cx - mark_pad, cy - mark_pad,
                              cx + mark_pad, cy + mark_pad,
                              outline=color, width=mark_w)

        # winning line strike-through
        if self.winning_line:
            a, _, cix = self.winning_line
            ra, ca = divmod(a, 3)
            rc, cc2 = divmod(cix, 3)
            ax = x0 + ca * cell + cell / 2
            ay = y0 + ra * cell + cell / 2
            bx = x0 + cc2 * cell + cell / 2
            by = y0 + rc * cell + cell / 2
            c.create_line(ax, ay, bx, by, fill=t["WIN_COLOR"], width=line_w + 1)

    def _on_board_click(self, event):
        if self.game_over or self._board_geom is None:
            return
        x0, y0, size = self._board_geom
        if not (x0 <= event.x <= x0 + size and y0 <= event.y <= y0 + size):
            return
        cell = size / 3
        cc = min(max(int((event.x - x0) // cell), 0), 2)
        r = min(max(int((event.y - y0) // cell), 0), 2)
        self._on_click(r * 3 + cc)

    def _on_board_hover(self, event):
        if event is None or self._board_geom is None:
            new_cell = None
        else:
            x0, y0, size = self._board_geom
            if x0 <= event.x <= x0 + size and y0 <= event.y <= y0 + size:
                cell = size / 3
                cc = min(max(int((event.x - x0) // cell), 0), 2)
                r = min(max(int((event.y - y0) // cell), 0), 2)
                new_cell = r * 3 + cc
            else:
                new_cell = None
        if new_cell != self._hover_cell:
            self._hover_cell = new_cell
            self._draw_board()

    # ---- New Game card ----
    def _build_newgame_card(self, parent):
        t = self.theme
        btn = RoundedButton(parent, t, "New Game", icon="play",
                             command=self._new_round, style="primary",
                             font=self.font_btn,
                             width=386, height=62)
        btn.pack(anchor="center")

    # ---- Players card ----
    def _build_players_card(self, parent):
        t = self.theme
        tk.Label(parent, text="Players", font=self.font_card_title,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(anchor="w", pady=(0, 14))

        self.player_rows = {}
        info = {"X": ("You", t["X_COLOR"]), "O": ("Opponent", t["O_COLOR"])}
        for idx, (mark, (sub, color)) in enumerate(info.items()):
            row = tk.Frame(parent, bg=t["SURFACE"])
            row.pack(fill="x", pady=6)

            avatar = tk.Canvas(row, width=44, height=44, bg=t["SURFACE"],
                                highlightthickness=0)
            avatar.pack(side="left")
            avatar.create_oval(1, 1, 43, 43, fill=color, outline="")
            self._draw_mark(avatar, 22, 22, 11, mark, t["SURFACE"])

            text_col = tk.Frame(row, bg=t["SURFACE"])
            text_col.pack(side="left", padx=12)
            tk.Label(text_col, text=f"Player {mark}", font=self.font_body_bold,
                     bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(anchor="w")
            tk.Label(text_col, text=sub, font=self.font_small,
                     bg=t["SURFACE"], fg=t["TEXT_SECONDARY"]).pack(anchor="w")

            dot = tk.Canvas(row, width=14, height=14, bg=t["SURFACE"],
                             highlightthickness=0)
            dot.pack(side="right")
            self.player_rows[mark] = dot

            if idx == 0:
                tk.Frame(parent, bg=t["DIVIDER"], height=1).pack(fill="x", pady=(4, 10))

    # ---- Game Status card ----
    def _build_status_card(self, parent):
        t = self.theme
        tk.Label(parent, text="Game Status", font=self.font_card_title,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(anchor="w", pady=(0, 10))

        self.status_canvas = tk.Canvas(parent, bg=t["SURFACE"], height=50,
                                        highlightthickness=0)
        self.status_canvas.pack(fill="x")
        self.status_canvas.bind("<Configure>", lambda e: self._draw_status())
        self._status_text = "Player X's Turn"

    def _draw_status(self):
        c = self.status_canvas
        c.delete("all")
        w = c.winfo_width() or 260
        h = c.winfo_height() or 54
        t = self.theme
        draw_rounded_rect(c, 1, 1, max(w - 1, 3), max(h - 1, 3), 16,
                           fill=t["STATUS_BG"], outline="")
        text_w = tkfont.Font(font=self.font_body_bold).measure(self._status_text)
        icon_size = 28
        gap = 18
        total_w = icon_size + gap + text_w
        start_x = max(22, (w - total_w) / 2)
        draw_icon_trophy(c, start_x + icon_size / 2, h / 2, icon_size,
                         t["PRIMARY_DARK"])
        c.create_text(start_x + icon_size + gap + text_w / 2, h / 2,
                      text=self._status_text,
                      font=self.font_body_bold, fill="#0F1210")

    # ---- Settings card ----
    def _build_settings_card(self, parent):
        t = self.theme
        header = tk.Frame(parent, bg=t["SURFACE"])
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Settings", font=self.font_card_title,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(side="left")
        gear = tk.Canvas(header, width=24, height=24, bg=t["SURFACE"], highlightthickness=0)
        gear.pack(side="right")
        draw_icon_gear(gear, 12, 12, 6, t["NEUTRAL"])

        tk.Label(parent, text="Theme", font=self.font_body,
                 bg=t["SURFACE"], fg=t["TEXT_SECONDARY"]).pack(anchor="w", pady=(0, 8))

        theme_row = tk.Frame(parent, bg=t["SURFACE"])
        theme_row.pack(fill="x", pady=(0, 16))
        theme_row.grid_columnconfigure(0, weight=1)
        theme_row.grid_columnconfigure(1, weight=1)

        self.btn_light = RoundedButton(
            theme_row, t, "Light",
            command=lambda: self._set_theme("light"),
            style="primary" if self.theme_name == "light" else "outline",
            width=100, height=40)
        self.btn_light.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_dark = RoundedButton(
            theme_row, t, "Dark",
            command=lambda: self._set_theme("dark"),
            style="primary" if self.theme_name == "dark" else "outline",
            width=100, height=40)
        self.btn_dark.grid(row=0, column=1, sticky="ew")

        tk.Frame(parent, bg=t["DIVIDER"], height=1).pack(fill="x", pady=(0, 16))

        sound_row = tk.Frame(parent, bg=t["SURFACE"])
        sound_row.pack(fill="x")
        tk.Label(sound_row, text="Sound", font=self.font_body,
                 bg=t["SURFACE"], fg=t["NEUTRAL"]).pack(side="left")
        self.sound_toggle = ToggleSwitch(sound_row, t, value=self.sound_on,
                                          command=self._set_sound)
        self.sound_toggle.pack(side="right")

    def _set_theme(self, name):
        if name == self.theme_name:
            return
        self.theme_name = name
        self.theme = LIGHT if name == "light" else DARK
        self._build_ui()
        self._update_ui()

    def _set_sound(self, value):
        self.sound_on = value

    # ------------------------------------------------------------------
    # GAME LOGIC
    # ------------------------------------------------------------------
    def _on_click(self, index):
        if self.game_over:
            return
        if self.board[index] != "":
            return
        self.board[index] = self.current_player
        if self.sound_on:
            try:
                self.root.bell()
            except Exception:
                pass

        win = self._check_winner()
        if win:
            self.winning_line = win
            self.scores[self.current_player] += 1
            self.game_over = True
        elif self._is_draw():
            self.game_over = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"

        self._update_ui()

    def _check_winner(self):
        for combo in WINNING_COMBINATIONS:
            a, b, c = combo
            if self.board[a] != "" and self.board[a] == self.board[b] == self.board[c]:
                return combo
        return None

    def _is_draw(self):
        return all(v != "" for v in self.board) and self.winning_line is None

    def _new_round(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.winning_line = None
        self.game_over = False
        self._hover_cell = None
        self._update_ui()

    def _reset_scores(self):
        self.scores = {"X": 0, "O": 0}
        self._new_round()

    # ------------------------------------------------------------------
    # UI REFRESH
    # ------------------------------------------------------------------
    def _update_ui(self):
        # status text
        if self.winning_line:
            self._status_text = f"Player {self.current_player} Wins!"
        elif self.game_over:
            self._status_text = "It's a Draw!"
        else:
            self._status_text = f"Player {self.current_player}'s Turn"
        if hasattr(self, "status_canvas"):
            self._draw_status()

        # scores
        if hasattr(self, "score_labels"):
            for mark, lbl in self.score_labels.items():
                lbl.config(text=str(self.scores[mark]))

        # active player indicator dots
        if hasattr(self, "player_rows"):
            t = self.theme
            for mark, dot in self.player_rows.items():
                dot.delete("all")
                active = (mark == self.current_player) and not self.game_over
                color = t["PRIMARY"] if active else t["DIVIDER"]
                dot.create_oval(1, 1, 13, 13, fill=color, outline="")

        # board
        if hasattr(self, "board_canvas"):
            self._draw_board()


# ----------------------------------------------------------------------------
def main():
  root = tk.Tk()
  app = TicTacToeApp(root)
  root.mainloop()


if __name__ == "__main__":
    main()
