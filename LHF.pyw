import os
import time
import queue

import pynput
import pyperclip

import formatter

os.system("title LaTeX Hotkey formatter")
controller = pynput.keyboard.Controller()

event_queue = queue.Queue()


# Keypress checker
def on_press(key):
    event_queue.put_nowait(("on_press", key, None))


def process_on_press(key):
    if str(data) == "<135>":
        try:
            highlighted = get_highlighted()
        except pyperclip.PyperclipTimeoutException:
            print("Could not copy to clipboard")
            return

        new_str = formatter.reformat(highlighted)
        paste_output(new_str)


def get_highlighted():
    old_clipboard = pyperclip.paste()
    pyperclip.copy("")

    with controller.pressed(pynput.keyboard.Key.ctrl):
        controller.touch("c", True)

    selected = pyperclip.waitForPaste(0.1)
    pyperclip.copy(old_clipboard)
    return selected


def paste_output(output):
    if output == "":
        controller.touch(pynput.keyboard.Key.backspace, True)
        return

    old_clipboard = pyperclip.paste()

    pyperclip.copy(output)
    with controller.pressed(pynput.keyboard.Key.ctrl):
        controller.touch("v", True)
        time.sleep(0.05)

    pyperclip.copy(old_clipboard)


# ----- Main ----- #
with pynput.keyboard.Listener(on_press=on_press) as listener:
    while True:
        event, data, return_queue = event_queue.get()

        try:
            if event == "on_press":
                process_on_press(data)
        except:
            pass

        if return_queue:
            return_queue.put(None)
