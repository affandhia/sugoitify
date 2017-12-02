import pygame
import math


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MusicBox(object, metaclass=Singleton):
    def __init__(self, volume=0.5):
        super()
        self.volume = volume
        self.pygame = pygame

        self.initMixer()

    def play_sound(self, soundfile):
        """Play sound through default mixer channel in blocking manner.
        This will load the whole sound into memory before playback
        """
        sound = self.pygame.mixer.Sound(soundfile)
        sound.play()

    def play_music(self, soundfile):
        """Stream music with mixer.music module in blocking manner.
        This will stream the sound from disk while playing.
        """
        self.pygame.mixer.music.load(soundfile)
        self.pygame.mixer.music.play()

    def stop_music(self):
        """stop currently playing music"""
        self.pygame.mixer.music.stop()

    def pause_music(self):
        self.pygame.mixer.music.pause()

    def unpause_music(self):
        self.pygame.mixer.music.unpause()

    def volume_up(self):
        self.volume = math.floor(self.volume) + 1
        self.volume = 1 if self.volume > 1 else self.volume

    def volume_down(self):
        self.volume = math.ceil(self.volume) - 1
        self.volume = 0 if self.volume < 0 else self.volume

    def getmixerargs(self):
        pygame.mixer.init()
        freq, size, chan = pygame.mixer.get_init()
        return freq, size, chan

    def initMixer(self):
        BUFFER = 3072  # audio buffer size, number of samples since pygame 1.8.
        FREQ, SIZE, CHAN = self.getmixerargs()
        self.pygame.mixer.init(FREQ, SIZE, CHAN, BUFFER)
