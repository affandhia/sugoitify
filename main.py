import time, threading, sys

from sugoitify.musicplayer import MusicBox
from sugoitify.utils import debounce
import RPi.GPIO as GPIO
from os import listdir
from os.path import isfile, join
from random import randint

debug = True if len(sys.argv) > 1 and sys.argv[1] == "debug" else False

mypath = 'src/music'
music_files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
debug and print(music_files)
box = MusicBox()
NO_REPEAT = "NO_REPEAT"
REPEAT_ALL = "REPEAT_ALL"
REPEAT_ONE = "REPEAT_ONE"
repeat_mode = [NO_REPEAT, REPEAT_ALL, REPEAT_ONE]
current_track_index = 0
repeat_mode_index = 0
shuffle = False
next_is_playing = False
playing = False
DEBOUNCE_THRESHOLD = 0.2

io_map = {
    "backward": {
        "pin": 10,
        "mode": GPIO.IN
    },
    "forward": {
        "pin": 9,
        "mode": GPIO.IN
    },
    "shuffle": {
        "pin": 11,
        "mode": GPIO.IN
    },
    "play": {
        "pin": 17,
        "mode": GPIO.IN
    },
    "stop": {
        "pin": 27,
        "mode": GPIO.IN
    },
    "repeat_mode": {
        "pin": 22,
        "mode": GPIO.IN
    },
    "vol_up": {
        "pin": 25,
        "mode": GPIO.IN
    },
    "vol_down": {
        "pin": 8,
        "mode": GPIO.IN
    },
    "vol_mute": {
        "pin": 7,
        "mode": GPIO.IN
    },
    "led_playing": {
        "pin": [23],
        "mode": GPIO.OUT
    },
    "led_muted": {
        "pin": 24,
        "mode": GPIO.OUT
    },
    "led_volume": {
        "pin": [2, 3, 4],
        "mode": GPIO.OUT
    },
    "led_repeat": {
        "pin": [14, 15],
        "mode": GPIO.OUT
    },
    "led_suffle": {
        "pin": 18,
        "mode": GPIO.OUT
    }
}


def adjust_led_volume():
    volume_pin = io_map["led_volume"]["pin"]
    shuffle_pin = io_map["led_suffle"]["pin"]
    repeat_mode_pin = io_map["led_repeat"]["pin"]

    for i in range(0, len(volume_pin)):
        volume = box.volume * 10
        if i * (10 / len(volume_pin)) < volume:
            GPIO.output(volume_pin[i], GPIO.HIGH)
        else:
            GPIO.output(volume_pin[i], GPIO.LOW)

    if repeat_mode[repeat_mode_index] == NO_REPEAT:
        GPIO.output(repeat_mode_pin, GPIO.LOW)
    elif repeat_mode[repeat_mode_index] == REPEAT_ONE:
        GPIO.output(repeat_mode_pin, [GPIO.HIGH, GPIO.LOW])
    elif repeat_mode[repeat_mode_index] == REPEAT_ALL:
        GPIO.output(repeat_mode_pin, [GPIO.HIGH, GPIO.HIGH])

    if shuffle:
        GPIO.output(shuffle_pin, GPIO.HIGH)
    else:
        GPIO.output(shuffle_pin, GPIO.LOW)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)

    GPIO.setwarnings(False)

    io_map_keys = io_map.keys()
    for key in io_map_keys:
        mode = io_map[key]["mode"]
        pin = io_map[key]["pin"]
        GPIO.setup(pin, mode, initial=GPIO.LOW) if mode == GPIO.OUT else GPIO.setup(pin, mode,
                                                                                    pull_up_down=GPIO.PUD_DOWN)


def cleanup_gpio():
    GPIO.cleanup()


def music_monitor():
    current_playing_led_index = 0
    #    nyala = False
    try:
        while True:
            time.sleep(1)
            playing_led = io_map["led_playing"]["pin"]
            #            GPIO.output(7, GPIO.HIGH if nyala else GPIO.LOW)
            #            nyala = not nyala
            if box.pygame.mixer.music.get_busy():
                for i in playing_led:
                    if i == playing_led[current_playing_led_index]:
                        GPIO.output(i, GPIO.HIGH)
                    else:
                        GPIO.output(i, GPIO.LOW)

                current_playing_led_index = 0 if current_playing_led_index + 1 >= len(playing_led) else (
                    current_playing_led_index + 1)
            else:
                GPIO.output(playing_led, GPIO.LOW)
                current_playing_led_index = 0

    except Exception as e:
        print("unknown error: {}".format(str(e)))
    finally:
        print("selesai")


def button_mapping():
    if GPIO.input(io_map["backward"]["pin"]):
        backward_button()
    elif GPIO.input(io_map["forward"]["pin"]):
        forward_button()
    elif GPIO.input(io_map["play"]["pin"]):
        pause_unpause_button()
    elif GPIO.input(io_map["stop"]["pin"]):
        stop_button()
    elif GPIO.input(io_map["repeat_mode"]["pin"]):
        repeat_mode_button()
    elif GPIO.input(io_map["shuffle"]["pin"]):
        shuffle_button()
    elif GPIO.input(io_map["vol_up"]["pin"]):
        vol_up_button()
    elif GPIO.input(io_map["vol_down"]["pin"]):
        vol_down_button()
    elif GPIO.input(io_map["vol_mute"]["pin"]):
        GPIO.output(24, GPIO.HIGH)
        vol_mute_button()
    elif debug:
        print("waiting input button")


def repeat_mode_mapping():
    global next_is_playing
    if repeat_mode[
        repeat_mode_index] == REPEAT_ALL and box.pygame.mixer.music.get_pos() <= -1 and playing and not next_is_playing:
        next_is_playing = True
        forward_button()
    elif repeat_mode[
        repeat_mode_index] == REPEAT_ONE and box.pygame.mixer.music.get_pos() <= -1 and playing and not next_is_playing:
        next_is_playing = True
        setup_music(music_files[current_track_index])


def controller():
    nyala = True
    while True:
        time.sleep(0.1)
        GPIO.output(23, GPIO.HIGH if nyala else GPIO.LOW)
        # nyala = not nyala
        button_mapping()
        repeat_mode_mapping()


@debounce(DEBOUNCE_THRESHOLD, debug)
def setup_music(path=music_files[0]):
    debug and print("index {} path: {}".format(current_track_index, path))
    box.play_music(path)

    adjust_led_volume()
    global next_is_playing
    next_is_playing = False


@debounce(DEBOUNCE_THRESHOLD, debug)
def backward_button():
    global playing, current_track_index, next_is_playing
    playing = True
    if box.pygame.mixer.music.get_pos() > 2000:
        setup_music(music_files[current_track_index])
    else:
        current_track_index = (len(music_files) - 1) if current_track_index <= 0 else (
            current_track_index - 1)
        setup_music(music_files[randint(0, len(music_files) - 1)]) if shuffle else setup_music(
            music_files[current_track_index])
        next_is_playing = False


@debounce(DEBOUNCE_THRESHOLD, debug)
def forward_button():
    global playing, current_track_index, next_is_playing
    playing = True
    current_track_index = 0 if current_track_index + 1 >= len(music_files) else (current_track_index + 1)
    setup_music(music_files[randint(0, len(music_files) - 1)]) if shuffle else setup_music(
        music_files[current_track_index])
    next_is_playing = False


@debounce(DEBOUNCE_THRESHOLD, debug)
def shuffle_button():
    global shuffle
    shuffle = not shuffle

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD, debug)
def pause_unpause_button():
    global playing
    playing = not playing
    if box.pygame.mixer.music.get_busy():
        box.pause_unpause_music()
    else:
        setup_music(music_files[current_track_index])


@debounce(DEBOUNCE_THRESHOLD, debug)
def stop_button():
    global playing
    playing = False
    box.stop_music()


@debounce(DEBOUNCE_THRESHOLD, debug)
def repeat_mode_button():
    global repeat_mode_index
    repeat_mode_index = 0 if repeat_mode_index + 1 >= len(repeat_mode) else (repeat_mode_index + 1)

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD, debug / 2)
def vol_up_button():
    box.volume_up()

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD, debug / 2)
def vol_down_button():
    box.volume_down()

    adjust_led_volume()


@debounce(DEBOUNCE_THRESHOLD, debug)
def vol_mute_button():
    box.volume_mute()
    GPIO.output(io_map["led_muted"]["pin"], GPIO.HIGH if box.muted else GPIO.LOW)


def main():
    setup_gpio()
    adjust_led_volume()

    gpio_thread = threading.Thread(target=music_monitor)
    gpio_thread.daemon = True
    gpio_thread.start()
    music_thread = threading.Thread(target=controller)
    music_thread.daemon = True
    music_thread.start()
    while True:
        if debug:
            if GPIO.input(io_map["vol_mute"]["pin"]):
                print("pencet")
            else:
                print("lepas")
        time.sleep(1)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    main()
