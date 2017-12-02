from sugoitify.musicplayer import MusicBox
import RPi.GPIO as GPIO


def main():
    box = MusicBox()
    try:
        filename = 'house_lo.wav'
        box.play_music(filename)
    except Exception:
        print("unknown error")

    print("Done")


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    main()