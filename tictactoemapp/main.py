"""
TicTacToe Mobile — Main Entry Point
Python + Kivy mobile-first application.
Manages ScreenManager, global state, and Android back-button navigation.

Run on Windows (desktop preview):
    py -3.12 main.py

Build Android APK:
    See README.md for Buildozer instructions.
"""

import os
import sys

# Configure mobile portrait window BEFORE importing Kivy modules
os.environ.setdefault("KIVY_NO_CONSOLELOG", "0")

from kivy.config import Config

# Only resize for desktop preview — Android ignores this
Config.set("graphics", "width", "390")
Config.set("graphics", "height", "844")
Config.set("graphics", "resizable", "1")
Config.set("graphics", "minimum_width", "320")
Config.set("graphics", "minimum_height", "568")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from game.game_state import GameState
from services.theme_manager import theme_manager
from services.sound_manager import sound_manager
from screens.home_screen import HomeScreen
from screens.game_mode_screen import GameModeScreen
from screens.game_screen import GameScreen
from screens.score_screen import ScoreScreen
from screens.settings_screen import SettingsScreen


class TicTacToeApp(App):
    """
    Main Kivy Application.
    Initializes global GameState, ScreenManager with all 5 screens,
    and wires Android hardware back-button navigation.
    """

    def build(self):
        self.title = "Tic Tac Toe"
        self.icon = "assets/images/appicon.png"

        # Global shared game state
        self.game_state = GameState()

        # Screen Manager with smooth slide transitions
        self.sm = ScreenManager(transition=SlideTransition(duration=0.22))

        # Register all screens
        self.sm.add_widget(HomeScreen(game_state=self.game_state, name="home"))
        self.sm.add_widget(GameModeScreen(game_state=self.game_state, name="game_mode"))
        self.sm.add_widget(GameScreen(game_state=self.game_state, name="gameplay"))
        self.sm.add_widget(ScoreScreen(game_state=self.game_state, name="score"))
        self.sm.add_widget(SettingsScreen(game_state=self.game_state, name="settings"))

        # Start on Home Screen
        self.sm.current = "home"

        # Android hardware back-button
        Window.bind(on_keyboard=self._handle_keyboard)

        return self.sm

    def _handle_keyboard(self, window, key, *args):
        """
        Handle Android hardware back button (key code 27 / ESC) and keyboard ESC.
        Navigates back through screen history.
        """
        BACK_KEY = 27  # ESC / Android back button

        if key == BACK_KEY:
            current = self.sm.current
            nav_map = {
                "gameplay": "game_mode",
                "game_mode": "home",
                "score": "home",
                "settings": "home",
            }
            if current in nav_map:
                self.sm.transition.direction = "right"
                self.sm.current = nav_map[current]
                return True  # Consumed — prevents app exit
            elif current == "home":
                # Allow normal OS back behavior (exit the app)
                return False

        return False

    def on_pause(self):
        """Android lifecycle: called when app moves to background."""
        return True

    def on_resume(self):
        """Android lifecycle: called when app returns to foreground."""
        pass


if __name__ == "__main__":
    TicTacToeApp().run()
