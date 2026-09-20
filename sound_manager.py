import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}

    def play_music(self, path, loop=-1, volume=0.5):
        """Carga y reproduce la música de fondo."""
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.stop()

    def load_sfx(self, name, path):
        """Carga un efecto de sonido corto (disparos, saltos, etc.)."""
        self.sounds[name] = pygame.mixer.Sound(path)

    def play_sfx(self, name, volume=0.7):
        """Reproduce un efecto de sonido cargado previamente."""
        if name in self.sounds:
            self.sounds[name].set_volume(volume)
            self.sounds[name].play()