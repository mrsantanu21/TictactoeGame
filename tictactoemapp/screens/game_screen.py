"""
Main Gameplay Screen (Screen 3).
Features responsive PlayerHeaderCard, interactive MobileGameBoard, New Game button,
and integrated GameOverDialog with sound and state reactivity.
Matches Screen 3 of the design reference.
"""

from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from services.theme_manager import theme_manager
from components.rounded_button import RoundedButton, IconButton
from components.player_card import PlayerHeaderCard
from components.game_board import MobileGameBoard
from components.custom_dialogs import GameOverDialog
from components.players_status_sheet import PlayersStatusSheet
from game.game_state import GameState


class GameScreen(Screen):
    """
    Screen 3: Main Gameplay Screen.
    """

    def __init__(self, game_state: GameState, **kwargs):
        super().__init__(**kwargs)
        self.game_state = game_state

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        # Background widget
        self.bg_widget = Widget(size_hint=(1, 1))
        self.bg_widget.bind(pos=self._draw_bg, size=self._draw_bg)
        self.root_layout.add_widget(self.bg_widget)

        # Content container
        self.content_layout = BoxLayout(
            orientation="vertical",
            padding=[24, 18, 24, 32],
            spacing=16,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.content_layout)

        # 1. HEADER (Back | "Tic Tac Toe" | Settings)
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52)
        self.btn_back = IconButton(icon="back", on_click=self._go_back)
        header.add_widget(self.btn_back)

        self.header_title = Label(
            text="Tic Tac Toe",
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

        # 2. PLAYER INFORMATION CARD
        self.player_card = PlayerHeaderCard()
        self.player_card.set_current_player(self.game_state.current_player)
        self.content_layout.add_widget(self.player_card)

        # 3. RESPONSIVE 3x3 GAME BOARD
        self.board_widget = MobileGameBoard(
            game_state=self.game_state,
            size_hint=(1, 1),
        )
        self.content_layout.add_widget(self.board_widget)

        # 4. BOTTOM NEW GAME BUTTON
        self.btn_new_game = RoundedButton(
            text="New Game",
            icon="play",
            style="primary",
            height=58,
            font_size="18sp",
            on_click=self._new_round,
        )
        self.content_layout.add_widget(self.btn_new_game)

        # 5. Game Over Dialog Modal
        self.game_over_dialog = GameOverDialog(
            on_play_again=self._new_round,
            on_home=self._go_home,
        )

        # 6. Status Sheet modal
        self.status_sheet = PlayersStatusSheet(game_state=self.game_state)
        self.root_layout.add_widget(self.status_sheet)

        self.game_state.add_listener(self._on_game_state_event)
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

    def _on_game_state_event(self, event: str, state: GameState):
        self.player_card.set_current_player(state.current_player)

        if event == "game_won":
            self.game_over_dialog.set_result(winner=state.current_player, is_draw=False)
            self.game_over_dialog.show(self.root_layout)
        elif event == "game_draw":
            self.game_over_dialog.set_result(winner=None, is_draw=True)
            self.game_over_dialog.show(self.root_layout)

    def _new_round(self):
        self.game_state.reset_board()
        self.player_card.set_current_player(self.game_state.current_player)

    def _go_back(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "game_mode"

    def _go_settings(self):
        if self.manager:
            self.manager.transition.direction = "left"
            self.manager.current = "settings"

    def _go_home(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "home"
