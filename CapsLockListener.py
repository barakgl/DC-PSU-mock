from functools import partial

from pynput import keyboard
from pynput.keyboard import Key


def on_press(func, key,):
    try:
        if key == Key.caps_lock:
            func()

    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def start_listen(target):

    func = partial(on_press, target)
    listener = keyboard.Listener(
        on_press=func)
    listener.start()
