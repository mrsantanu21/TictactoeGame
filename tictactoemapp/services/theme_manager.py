"""
Theme Manager for Tic-Tac-Toe Mobile.
Centralized color palette management for Light and Dark themes.
Provides reactive callbacks and RGBA color tuples for Kivy.
"""

from typing import Callable, Dict, List
from kivy.utils import get_color_from_hex
from kivy.core.window import Window


class ThemeManager:
    """
    Manages Light and Dark color schemes.
    Notifies registered listeners whenever theme changes.
    """

    LIGHT_HEX = {
        "BACKGROUND": "#F6F1E8",
        "SURFACE": "#FBF7F0",
        "PRIMARY": "#5F7865",
        "PRIMARY_LIGHT": "#DCE6D8",
        "PRIMARY_TEXT": "#26342F",
        "SECONDARY_TEXT": "#66706A",
        "BORDER": "#DED8CD",
        "WINNING_ACCENT": "#A67B5B",
        "X_COLOR": "#26342F",
        "O_COLOR": "#5F7865",
        "CARD_SHADOW": "#00000010",
        "ON_PRIMARY": "#FFFFFF",
        "OVERLAY": "#00000066",
    }

    DARK_HEX = {
        "BACKGROUND": "#242622",
        "SURFACE": "#323630",
        "PRIMARY": "#8DA58D",
        "PRIMARY_LIGHT": "#435244",
        "PRIMARY_TEXT": "#F4F0E8",
        "SECONDARY_TEXT": "#B8B8AE",
        "BORDER": "#484B45",
        "WINNING_ACCENT": "#C79A72",
        "X_COLOR": "#F4F0E8",
        "O_COLOR": "#8DA58D",
        "CARD_SHADOW": "#00000040",
        "ON_PRIMARY": "#1F221E",
        "OVERLAY": "#00000088",
    }

    def __init__(self, default_theme: str = "light"):
        self.current_theme: str = default_theme
        self._listeners: List[Callable[["ThemeManager"], None]] = []
        self._sync_window_clearcolor()

    @property
    def is_dark(self) -> bool:
        return self.current_theme == "dark"

    @property
    def tokens(self) -> Dict[str, str]:
        """Returns hex dictionary for current theme."""
        return self.DARK_HEX if self.is_dark else self.LIGHT_HEX

    def get(self, token_name: str) -> List[float]:
        """Returns RGBA color tuple (0.0 - 1.0) for Kivy."""
        hex_val = self.tokens.get(token_name, "#000000")
        return get_color_from_hex(hex_val)

    def get_hex(self, token_name: str) -> str:
        """Returns hex color string."""
        return self.tokens.get(token_name, "#000000")

    def set_theme(self, theme_name: str) -> None:
        """Sets active theme ('light' or 'dark') and notifies listeners."""
        if theme_name in ("light", "dark") and theme_name != self.current_theme:
            self.current_theme = theme_name
            self._sync_window_clearcolor()
            self._notify_listeners()

    def toggle_theme(self) -> None:
        """Toggles between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)

    def add_listener(self, callback: Callable[["ThemeManager"], None]) -> None:
        """Register a callback when theme changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[["ThemeManager"], None]) -> None:
        """Remove a previously registered theme callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _sync_window_clearcolor(self) -> None:
        """Updates Kivy window clearcolor."""
        try:
            Window.clearcolor = self.get("BACKGROUND")
        except Exception:
            pass

    def _notify_listeners(self) -> None:
        """Dispatches theme update to all registered widgets and screens."""
        for listener in list(self._listeners):
            try:
                listener(self)
            except Exception as ex:
                print(f"[ThemeManager._notify_listeners] Error notifying: {ex}")


# Global singleton instance
theme_manager = ThemeManager("light")
