import os
import time

import pynput
import pyperclip

import formatter

os.system("title LaTeX Hotkey formatter")
controller = pynput.keyboard.Controller()


# Keypress checker
def on_press(key):
    if str(key) == "<135>":
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
    old_clipboard = pyperclip.paste()

    pyperclip.copy(output)
    with controller.pressed(pynput.keyboard.Key.ctrl):
        controller.touch("v", True)
        time.sleep(0.05)

    pyperclip.copy(old_clipboard)


# ----- Main ----- #
with pynput.keyboard.Listener(on_press=on_press) as listener:
    listener.join()
