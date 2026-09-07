# Tic Tac Toe — Mobile Android App (Python + Kivy)

[![Build APK](https://github.com/mrsantanu21/TictactoeGame/actions/workflows/build-apk.yml/badge.svg)](https://github.com/mrsantanu21/TictactoeGame/actions/workflows/build-apk.yml)
[![Download Latest APK](https://img.shields.io/badge/Download-Latest%20APK-brightgreen?logo=android)](https://github.com/mrsantanu21/TictactoeGame/releases/latest)

> 📱 **Download APK**: You can download the latest Android `.apk` directly from the [GitHub Releases Page](https://github.com/mrsantanu21/TictactoeGame/releases/latest).

A polished mobile-first Tic-Tac-Toe app converted from the original Windows desktop Tkinter application.
Built entirely in **Python + Kivy**, designed for Android, with a clean six-screen UI.

---

## 📁 Project Structure

```
tictactoemapp/
├── main.py                    # App entry point
├── game/
│   ├── game_logic.py          # Pure game logic (no UI, testable)
│   └── game_state.py          # GameState with observer callbacks
├── screens/
│   ├── home_screen.py         # Screen 1: Home
│   ├── game_mode_screen.py    # Screen 2: Game Mode
│   ├── game_screen.py         # Screen 3: Gameplay
│   ├── score_screen.py        # Screen 5: Scores
│   └── settings_screen.py    # Screen 6: Settings
├── components/
│   ├── rounded_button.py      # Mobile-first rounded buttons
│   ├── player_card.py         # Player header card with turn indicator
│   ├── game_board.py          # Canvas-drawn responsive 3x3 board
│   ├── players_status_sheet.py # Bottom sheet panel
│   └── custom_dialogs.py      # Game Over & Confirm dialogs
├── services/
│   ├── theme_manager.py       # Light/Dark theme system
│   └── sound_manager.py       # Sound with auto WAV generation
├── tests/
│   └── test_game_logic.py     # 13 automated unit tests
├── assets/sounds/             # Auto-generated WAV sound effects
├── requirements.txt
├── buildozer.spec
└── README.md
```

---

## 🎮 Features

| Feature | Status |
|---|---|
| Player vs Player | ✅ Fully working |
| Player vs AI | 🔜 Coming Soon (badge displayed) |
| Win detection (8 combos) | ✅ |
| Draw detection | ✅ |
| Score tracking | ✅ Persists across rounds |
| Reset Scores (with confirmation) | ✅ |
| New Game (keeps scores) | ✅ |
| Light Theme | ✅ |
| Dark Theme | ✅ |
| Live theme switching | ✅ Instant across all screens |
| Sound effects | ✅ Auto-generated WAV |
| Sound ON/OFF toggle | ✅ |
| Game Over dialog | ✅ Play Again / Home |
| Bottom Sheet (Players & Status) | ✅ |
| Android Back Button | ✅ |
| Responsive board | ✅ Works on any screen size |
| Animations (mark scale-in) | ✅ |
| 13 Automated tests | ✅ |

---

## 🎨 Color Palette

### Light Theme
- Background: `#F6F1E8` (Warm cream)
- Primary: `#5F7865` (Forest green)
- Surface: `#FBF7F0`
- Winning Accent: `#A67B5B` (Warm brown)

### Dark Theme
- Background: `#242622`
- Primary: `#8DA58D` (Sage green)
- Winning Accent: `#C79A72`
<img width="1024" height="1536" alt="UI" src="https://github.com/user-attachments/assets/376bca55-bc3c-4d5a-866d-dc5be8997e22" />
