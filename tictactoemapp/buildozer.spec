[app]
# App name and package
title = Tic Tac Toe
package.name = tictactoe
package.domain = com.mrsantanu21

# Source configuration
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav

# Application version
version = 1.0.0

# Python requirements
requirements = python3,kivy

# Icon and presplash
icon.filename = %(source.dir)s/assets/images/appicon.png
presplash.filename = %(source.dir)s/assets/images/presplash.png

# Orientation
orientation = portrait

# Android API levels
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
# android.sdk is deprecated and omitted in favor of android.api
android.accept_sdk_license = True
android.skip_update = False

# Android permissions
android.permissions = INTERNET,VIBRATE

# Android build modes
android.archs = arm64-v8a, armeabi-v7a

# Enable fullscreen
fullscreen = 0

# Android activity class
android.activity_class_name = org.kivy.android.PythonActivity

# Excluded paths and desktop-only files
source.exclude_dirs = tests, .git, __pycache__, assets/images/raw, .venv, .vscode, .github, .agents
source.exclude_patterns = twindowstictactoe.py, *.pyc

[buildozer]
log_level = 2
warn_on_root = 1
