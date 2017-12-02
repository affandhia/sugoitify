from sugoitify.musicplayer import MusicBox
import RPi.GPIO as GPIO

def main():
    box = MusicBox()
    try:
        filename = 'house_lo.wav'
        box.play_music(filename)
    except KeyboardInterrupt:  # to stop playing, press "ctrl-c"
        box.stop_music()
        print("\nPlay Stopped by user")
    except Exception:
        print("unknown error")

    print("Done")


if __name__ == '__main__':
    # import logging

    # logging.basicConfig(level=logging.DEBUG)

    main()