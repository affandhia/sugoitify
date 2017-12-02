import time, threading

from sugoitify.musicplayer import MusicBox
from sugoitify.utils import Throttle, debounce
import RPi.GPIO as GPIO

box = MusicBox()
io_map = {
    "rewind": 29,
    "play": 31,
    "stop": 33,
    "vol_up": 35,
    "vol_down": 37,
    "led_playing": 8,
}


@Throttle(seconds=0.5)
def printOutput():
    print("throttled")


@debounce(3)
def printOutputan():
    print("debounced")


def setup_music():
    filename = 'src/music/house_lo.wav'
    box.play_music(filename)


def setup_GPIO():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setwarnings(False)

    GPIO.setup(io_map["led_playing"], GPIO.OUT)
    GPIO.setup(io_map["rewind"], GPIO.IN)
    GPIO.setup(io_map["play"], GPIO.IN)
    GPIO.setup(io_map["stop"], GPIO.IN)
    GPIO.setup(io_map["vol_up"], GPIO.IN)
    GPIO.setup(io_map["vol_down"], GPIO.IN)


def cleanup_GPIO():
    GPIO.cleanup()


def music_monitor():
    try:
        while box.pygame.mixer.music.get_busy():
            GPIO.output(io_map["led_playing"], GPIO.HIGH)
            time.sleep(1)

            GPIO.output(io_map["led_playing"], GPIO.LOW)
            time.sleep(1)
    except Exception as e:
        print("unknown error: {}".format(str(e)))
    finally:
        print("selesai")


def main():
    setup_GPIO()
    setup_music()
    printOutputan()
    while True:
        printOutput()

    print("Done")


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    main()
