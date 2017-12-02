import time, threading

from sugoitify.musicplayer import MusicBox
from sugoitify.utils import debounce
import RPi.GPIO as GPIO
from os import listdir
from os.path import isfile, join

mypath = 'src/music'
music_files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
print(music_files)
box = MusicBox()
io_map = {
    "backward": {
        "pin": 16,
        "mode": GPIO.IN
    },
    "forward": {
        "pin": 18,
        "mode": GPIO.IN
    },
    "play": {
        "pin": 8,
        "mode": GPIO.IN
    },
    "stop": {
        "pin": 10,
        "mode": GPIO.IN
    },
    "repeat_mode": {
        "pin": 12,
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
    "vol_mute": {
        "pin": 15,
        "mode": GPIO.IN
    },
    "led_playing": {
        "pin": [36, 38, 40],
        "mode": GPIO.OUT
    },
    "led_muted": {
        "pin": 32,
        "mode": GPIO.OUT
    },
    "led_volume": {
        "pin": [29, 31, 33, 35, 37],
        "mode": GPIO.OUT
    }
}
current_track_index = 0
DEBOUNCE_THRESHOLD = 0.2


def adjust_led_volume():
    for i in range(0, 5):
        if i * 2 < box.volume * 10:
            GPIO.output(io_map["led_volume"]["pin"][i], GPIO.HIGH)
        else:
            GPIO.output(io_map["led_volume"]["pin"][i], GPIO.LOW)


@debounce(DEBOUNCE_THRESHOLD)
def setup_music(path=music_files[0]):
    print("index {} path: {}".format(current_track_index, path))
    box.play_music(path)

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
    current_led = 0
    pin = io_map["led_playing"]["pin"]
    try:
        while True:
            time.sleep(1)

            if box.pygame.mixer.music.get_busy():
                for i in pin:
                    if i == pin[current_led]:
                        GPIO.output(i, GPIO.HIGH)
                    else:
                        GPIO.output(i, GPIO.LOW)

                current_led = 0 if current_led + 1 >= len(pin) else (current_led + 1)
            else:
                GPIO.output(pin, GPIO.LOW)
                current_led = 0
    except Exception as e:
        print("unknown error: {}".format(str(e)))
    finally:
        print("selesai")


def controller():
    while True:
        time.sleep(0.1)
        # print("Position: {}".format(box.pygame.mixer.music.get_pos()))
        if GPIO.input(io_map["backward"]["pin"]):
            backward_button()
        if GPIO.input(io_map["forward"]["pin"]):
            forward_button()
        elif GPIO.input(io_map["play"]["pin"]):
            pause_unpause_button()
        elif GPIO.input(io_map["stop"]["pin"]):
            stop_button()
        elif GPIO.input(io_map["vol_up"]["pin"]):
            vol_up_button()
        elif GPIO.input(io_map["vol_down"]["pin"]):
            vol_down_button()
        elif GPIO.input(io_map["vol_mute"]["pin"]):
            vol_mute_button()


@debounce(DEBOUNCE_THRESHOLD)
def backward_button():
    global current_track_index
    if box.pygame.mixer.music.get_pos() > 2000:
        setup_music(music_files[current_track_index])
    else:
        current_track_index = (len(music_files) - 1) if current_track_index <= 0 else (
            current_track_index - 1)
        setup_music(music_files[current_track_index])


@debounce(DEBOUNCE_THRESHOLD)
def forward_button():
    global current_track_index
    current_track_index = 0 if current_track_index + 1 >= len(music_files) else (current_track_index + 1)
    setup_music(music_files[current_track_index])


@debounce(DEBOUNCE_THRESHOLD)
def pause_unpause_button():
    if box.pygame.mixer.music.get_busy():
        box.pause_unpause_music()
    else:
        setup_music(music_files[current_track_index])


@debounce(DEBOUNCE_THRESHOLD)
def stop_button():
    box.stop_music()


@debounce(DEBOUNCE_THRESHOLD / 2)
def vol_up_button():
    box.volume_up()

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD / 2)
def vol_down_button():
    box.volume_down()

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD)
def vol_mute_button():
    box.volume_mute()

    GPIO.output(io_map["led_muted"]["pin"], GPIO.HIGH if box.muted else GPIO.LOW)


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
