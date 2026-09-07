"""
dp_utils.py — Responsive UI Scaling Utilities
==============================================
Provides density-independent and viewport-relative sizing helpers for all
UI components and screens in the TicTacToe mobile app.

Usage:
    from services.dp_utils import dp, sp, sh, sw, scaled_h, clamp

    height = scaled_h(56)       # Scales a 56dp height with viewport height
    size   = (dp(44), dp(44))   # Density-independent 44x44 widget
    sheet  = sh(0.60)           # 60% of screen height
    font   = sp(17)             # Density-scaled font size (same as "17sp")
"""

from kivy.metrics import dp as _dp, sp as _sp
from kivy.core.window import Window

# ── Reference design viewport (portrait iPhone-size reference) ──────────────
_REF_WIDTH  = 390.0   # dp
_REF_HEIGHT = 844.0   # dp


def dp(value: float) -> float:
    """
    Convert a density-independent pixel value to actual screen pixels.

    Wraps Kivy's built-in dp() which automatically scales with the device
    DPI (160 dpi baseline). Use for all widget sizes, padding, spacing,
    border widths, and icon sizes.
    """
    return _dp(value)


def sp(value: float) -> float:
    """
    Convert a scale-independent pixel value to actual screen pixels.

    Wraps Kivy's built-in sp() which scales with both device DPI and the
    user's system font-size preference. Use for font sizes only.
    """
    return _sp(value)


def sw(fraction: float) -> float:
    """
    Return a fraction of the current screen width in pixels.

    Example:
        sw(0.84)  → 84% of screen width
    """
    return Window.width * fraction


def sh(fraction: float) -> float:
    """
    Return a fraction of the current screen height in pixels.

    Example:
        sh(0.60)  → 60% of screen height  (good for bottom sheets)
    """
    return Window.height * fraction


def scaled_h(base_dp: float, min_scale: float = 0.78, max_scale: float = 1.30) -> float:
    """
    Scale a base height (in dp) proportionally with the device's viewport height.

    On the reference device (844dp tall) this returns exactly dp(base_dp).
    On a taller device (e.g. 932dp) the result is slightly larger.
    On a shorter device (e.g. 640dp) the result is slightly smaller.

    Args:
        base_dp:   The reference height in density-independent pixels.
        min_scale: Minimum allowed scaling factor (default 0.78).
        max_scale: Maximum allowed scaling factor (default 1.30).

    Example:
        scaled_h(56)   → dp(56) on 844dp screen, slightly bigger on 6.7" phone
    """
    ratio = Window.height / _REF_HEIGHT
    scale = clamp(ratio, min_scale, max_scale)
    return _dp(base_dp) * scale


def clamp(value: float, lo: float, hi: float) -> float:
    """Return value clamped to [lo, hi]."""
    return max(lo, min(value, hi))
