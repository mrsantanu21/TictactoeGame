# Tic Tac Toe — Mobile Android App (Python + Kivy)

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

## 🚀 Run on Windows (Desktop Preview)

### Prerequisites

1. **Python 3.12** (recommended — Kivy has prebuilt wheels for 3.12)
2. Install Kivy:

```bash
py -3.12 -m pip install kivy
```

### Launch the App

```bash
cd path\to\tictactoemapp
py -3.12 main.py
```

A **390×844** portrait window opens — matching mobile dimensions.

---

## 🧪 Run Automated Tests

Tests run independently of Kivy (no window required):

```bash
py -3.12 tests\test_game_logic.py -v
```

Expected output: **13 tests, all OK**.

---

## 📱 Build Android APK

### Requirements for APK Build

Building an Android APK requires a Linux environment (natively or via WSL2).

### Option A: WSL2 on Windows 10/11

1. Install WSL2 with Ubuntu:
```bash
wsl --install
```

2. Inside WSL2 Ubuntu:
```bash
sudo apt update && sudo apt install -y python3-pip openjdk-17-jdk git zip unzip
pip3 install buildozer
```

3. Copy the project into WSL2, then:
```bash
cd /path/to/tictactoemapp
buildozer android debug
```

4. The APK will be at:
```
bin/tictactoe-1.0.0-debug.apk
```

### Option B: GitHub Actions (Cloud Build)

Create `.github/workflows/build.yml`:
```yaml
name: Build APK
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install buildozer cython
      - run: buildozer android debug
      - uses: actions/upload-artifact@v3
        with:
          name: apk
          path: bin/*.apk
```

---

## 📲 Install APK on Android

1. Enable **Developer Options** → **USB Debugging** on your phone.
2. Connect via USB.
3. Install using ADB:
```bash
adb install bin/tictactoe-1.0.0-debug.apk
```

Or transfer the `.apk` file to the phone and install it directly (allow Unknown Sources).

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
