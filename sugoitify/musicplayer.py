import pygame
import math


class MusicBox(object):
    def __init__(self, volume=0.5):
        super()
        self.initMixer()
        self.volume = volume

    def play_sound(self, soundfile):
        """Play sound through default mixer channel in blocking manner.
        This will load the whole sound into memory before playback
        """
        clock = pygame.time.Clock()
        sound = pygame.mixer.Sound(soundfile)
        sound.play()
        while pygame.mixer.get_busy():
            print("Playing...")
            clock.tick(1000)

    def play_music(self, soundfile):
        """Stream music with mixer.music module in blocking manner.
        This will stream the sound from disk while playing.
        """
        clock = pygame.time.Clock()
        pygame.mixer.music.load(soundfile)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            print("Playing...")
            clock.tick(1000)

    def stop_music(self):
        """stop currently playing music"""
        pygame.mixer.music.stop()

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
        pygame.mixer.init(FREQ, SIZE, CHAN, BUFFER)
