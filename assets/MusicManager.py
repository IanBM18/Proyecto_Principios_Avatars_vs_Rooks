import pygame
import os

class MusicManager:
    _instance = None  # Singleton: asegura que solo haya una instancia global

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicManager, cls).__new__(cls)
            pygame.mixer.init()
            cls._instance.soundtracks = [
                "assets/sounds/bright_song.mp3",
                "assets/sounds/sci-fi_puzzle_in-game_3_bpm100.mp3"
            ]
            cls._instance.current_index = 0
            cls._instance.volume = 0.5
            cls._instance.playing = False
            cls._instance.music_enabled = True
        return cls._instance

    # -------------------------------------------------
    # 🔊 Reproduce una pista de fondo según índice
    # -------------------------------------------------
    def play(self, soundtrack_index=1, volume=None):
        """Reproduce la música indicada (por índice desde 1)."""
        if not self.music_enabled:
            return

        idx = soundtrack_index - 1
        if 0 <= idx < len(self.soundtracks):
            track_path = self.soundtracks[idx]
            if os.path.exists(track_path):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(track_path)
                if volume is not None:
                    pygame.mixer.music.set_volume(volume)
                    self.volume = volume
                else:
                    pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)
                self.current_index = idx
                self.playing = True

    # -------------------------------------------------
    # 🎵 Cambia la pista actual y sigue sonando
    # -------------------------------------------------
    def change_track(self, soundtrack_index):
        """Cambia de pista sin detener la música."""
        self.play(soundtrack_index, self.volume)

    # -------------------------------------------------
    # 🔉 Cambia el volumen dinámicamente
    # -------------------------------------------------
    def set_volume(self, volume):
        """Cambia el volumen sin reiniciar la pista."""
        pygame.mixer.music.set_volume(volume)
        self.volume = volume

    # -------------------------------------------------
    # ⏸ Pausar o detener la música
    # -------------------------------------------------
    def stop(self):
        """Detiene completamente la música."""
        pygame.mixer.music.stop()
        self.playing = False

    # -------------------------------------------------
    # ▶️ Pausar y reanudar música
    # -------------------------------------------------
    def pause(self):
        """Pausa la música si está sonando."""
        if self.playing:
            pygame.mixer.music.pause()

    def resume(self):
        """Reanuda la música pausada."""
        pygame.mixer.music.unpause()

    # -------------------------------------------------
    # 🎚 Habilitar o deshabilitar música globalmente
    # -------------------------------------------------
    def toggle_music(self, enabled: bool):
        """Activa o desactiva toda la música."""
        self.music_enabled = enabled
        if not enabled:
            self.stop()
        elif not self.playing:
            self.play(self.current_index + 1, self.volume)