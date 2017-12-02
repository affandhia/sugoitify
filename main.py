import pygame
from sugoitify.musicplayer import MusicBox
import RPi.GPIO as GPIO

def main():
    try:
        box = MusicBox()
        filename = 'house_lo.wav'
        box.playmusic(filename)
    except KeyboardInterrupt:  # to stop playing, press "ctrl-c"
        box.stopmusic()
        print("\nPlay Stopped by user")
    except Exception:
        print("unknown error")

    print("Done")


if __name__ == '__main__':
    # import logging

    # logging.basicConfig(level=logging.DEBUG)

    main()