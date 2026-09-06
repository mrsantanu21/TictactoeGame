"""
Sound Manager for Tic-Tac-Toe Mobile.
Handles audio playback for moves, wins, and draws.
Includes fallback audio generation using standard library wave module.
Safe for Android read-only bundles and headless/silent environments.
"""

import math
import os
import struct
import wave
from typing import Dict, Optional
from kivy.core.audio import Sound, SoundLoader
from kivy.app import App


class SoundManager:
    """
    Manages sound effects with volume and mute toggles.
    Generates pleasant clean WAV sounds automatically if not present.
    """

    def __init__(self, sound_enabled: bool = True):
        self.sound_enabled: bool = sound_enabled
        self._sounds: Dict[str, Optional[Sound]] = {}
        self._sound_dir: str = self._get_sound_directory()
        self._ensure_sound_files()
        self._load_sounds()

    def _get_sound_directory(self) -> str:
        """
        Determines a safe directory for sound files.
        Tries local assets/sounds first; falls back to user_data_dir on Android.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_sound_dir = os.path.join(base_dir, "assets", "sounds")

        # Try creating/writing to assets_sound_dir
        try:
            os.makedirs(assets_sound_dir, exist_ok=True)
            test_file = os.path.join(assets_sound_dir, ".test_write")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return assets_sound_dir
        except Exception:
            pass

        # Fallback to app's writable user_data_dir on Android
        try:
            app = App.get_running_app()
            if app and hasattr(app, "user_data_dir"):
                user_sound_dir = os.path.join(app.user_data_dir, "sounds")
                os.makedirs(user_sound_dir, exist_ok=True)
                return user_sound_dir
        except Exception:
            pass

        fallback = os.path.join(os.path.expanduser("~"), ".tictactoe_sounds")
        os.makedirs(fallback, exist_ok=True)
        return fallback

    def _synthesize_wav(self, file_path: str, tones: list, sample_rate: int = 44100) -> None:
        """
        Synthesizes a PCM 16-bit mono WAV file with smooth attack/decay envelope.
        tones is a list of tuples: (freq_start, freq_end, duration_sec, amplitude)
        """
        try:
            total_samples = []
            for freq_start, freq_end, duration, amp in tones:
                num_samples = int(sample_rate * duration)
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    # Linear frequency sweep
                    freq = freq_start + (freq_end - freq_start) * (t / duration)
                    # Envelope (fade in 5%, fade out 20%)
                    fade_in = min(1.0, i / max(1, int(num_samples * 0.08)))
                    fade_out = min(1.0, (num_samples - i) / max(1, int(num_samples * 0.25)))
                    envelope = fade_in * fade_out
                    sample = amp * envelope * math.sin(2.0 * math.pi * freq * t)
                    total_samples.append(int(sample * 32767.0))

            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(1)  # mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                data = struct.pack(f"<{len(total_samples)}h", *total_samples)
                wf.writeframes(data)
        except Exception as ex:
            print(f"[SoundManager._synthesize_wav] Could not generate {file_path}: {ex}")

    def _ensure_sound_files(self) -> None:
        """Ensures move_x, move_o, win, and draw sound files exist."""
        specs = {
            "move_x.wav": [(600, 780, 0.07, 0.45)],
            "move_o.wav": [(480, 560, 0.07, 0.45)],
            "win.wav": [
                (523.25, 523.25, 0.10, 0.45),  # C5
                (659.25, 659.25, 0.10, 0.45),  # E5
                (783.99, 783.99, 0.22, 0.55),  # G5
            ],
            "draw.wav": [
                (440.0, 390.0, 0.12, 0.35),
                (349.0, 310.0, 0.18, 0.35),
            ],
        }

        for filename, tones in specs.items():
            path = os.path.join(self._sound_dir, filename)
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                self._synthesize_wav(path, tones)

    def _load_sounds(self) -> None:
        """Loads available sound files using Kivy SoundLoader."""
        sound_names = ["move_x", "move_o", "win", "draw"]
        for name in sound_names:
            path = os.path.join(self._sound_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    sound = SoundLoader.load(path)
                    if sound:
                        sound.volume = 0.8
                    self._sounds[name] = sound
                except Exception as ex:
                    print(f"[SoundManager._load_sounds] Failed loading {name}: {ex}")
                    self._sounds[name] = None
            else:
                self._sounds[name] = None

    def play(self, sound_name: str) -> None:
        """Plays specified sound effect if sound is enabled."""
        if not self.sound_enabled:
            return
        sound = self._sounds.get(sound_name)
        if sound:
            try:
                if sound.state == "play":
                    sound.stop()
                sound.play()
            except Exception as ex:
                print(f"[SoundManager.play] Error playing {sound_name}: {ex}")

    def set_enabled(self, enabled: bool) -> None:
        """Toggles sound on or off."""
        self.sound_enabled = enabled


# Global singleton instance
sound_manager = SoundManager(sound_enabled=True)
