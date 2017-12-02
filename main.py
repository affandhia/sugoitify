import time, threading

from sugoitify.musicplayer import MusicBox
from sugoitify.utils import debounce
import RPi.GPIO as GPIO

box = MusicBox()
io_map = {
    "rewind": {
        "pin": 12,
        "mode": GPIO.IN
    },
    "play": {
        "pin": 16,
        "mode": GPIO.IN
    },
    "stop": {
        "pin": 18,
        "mode": GPIO.IN
    },
    "vol_up": {
        "pin": 11,
        "mode": GPIO.IN
    },
    "vol_down": {
        "pin": 13,
        "mode": GPIO.IN
    },
    "mute": {
        "pin": 15,
        "mode": GPIO.IN
    },
    "led_playing": {
        "pin": 8,
        "mode": GPIO.OUT
    },
    "led_volume": {
        "pin": [29, 31, 33, 35, 37],
        "mode": GPIO.OUT
    }
}
DEBOUNCE_THRESHOLD = 0.2


def adjust_led_volume():
    for i in range(0, 5):
        if i * 2 < box.volume * 10:
            GPIO.output(io_map["led_volume"]["pin"][i], GPIO.HIGH)
        else:
            GPIO.output(io_map["led_volume"]["pin"][i], GPIO.LOW)


@debounce(DEBOUNCE_THRESHOLD)
def setup_music():
    filename = 'src/music/house_lo.wav'
    box.play_music(filename)

    adjust_led_volume()


def setup_GPIO():
    GPIO.setmode(GPIO.BOARD)

    GPIO.setwarnings(False)

    io_map_keys = io_map.keys()
    for key in io_map_keys:
        mode = io_map[key]["mode"]
        pin = io_map[key]["pin"]
        GPIO.setup(pin, mode) if mode == GPIO.OUT else GPIO.setup(pin, mode, pull_up_down=GPIO.PUD_DOWN)


def cleanup_GPIO():
    GPIO.cleanup()


def music_monitor():
    try:
        while True:
            time.sleep(0.01)

            if box.pygame.mixer.music.get_busy():
                GPIO.output(io_map["led_playing"]["pin"], GPIO.HIGH)
            else:
                GPIO.output(io_map["led_playing"]["pin"], GPIO.LOW)
    except Exception as e:
        print("unknown error: {}".format(str(e)))
    finally:
        print("selesai")


def controller():
    while True:
        time.sleep(0.1)

        if GPIO.input(io_map["rewind"]["pin"]):
            setup_music()
        elif GPIO.input(io_map["play"]["pin"]):
            pause_unpause_button()
        elif GPIO.input(io_map["stop"]["pin"]):
            stop_button()
        elif GPIO.input(io_map["vol_up"]["pin"]):
            vol_up_button()
        elif GPIO.input(io_map["vol_down"]["pin"]):
            vol_down_button()


@debounce(DEBOUNCE_THRESHOLD)
def pause_unpause_button():
    box.pause_unpause_music()


@debounce(DEBOUNCE_THRESHOLD)
def stop_button():
    box.stop_music()


@debounce(DEBOUNCE_THRESHOLD)
def vol_up_button():
    box.volume_up()

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD)
def vol_down_button():
    box.volume_down()

    adjust_led_volume()


def main():
    setup_GPIO()
    setup_music()

    gpio_thread = threading.Thread(target=music_monitor)
    gpio_thread.daemon = True
    gpio_thread.start()
    music_thread = threading.Thread(target=controller)
    music_thread.daemon = True
    music_thread.start()


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    main()
