import configparser
import ctypes
import ctypes.wintypes
import os
import re
import sys

import config
import font_manager

if sys.platform in ("linux", "linux2"):
    raise NotImplementedError(f"Linux is not currently supported")
elif sys.platform in ("Windows", "win32", "cygwin"):
    pass
else:
    raise EnvironmentError(f"Unknown platform {sys.platform}")


class Context:
    def __init__(self, executable, window_title, entry):
        self.executable = executable
        self.window_title = window_title

        self.font_info = self._get_font_info(entry["font"])
        self.tabsize = float(entry["tabsize"])

    @staticmethod
    def _get_font_info(family_names):
        if family_names == "MONOSPACED":
            return font_manager.FontInfo(None, monospaced=True)

        families = family_names.split(", ")
        families.extend(default_entry["font"].split(", "))
        families = tuple(None if family == "sans-serif" else family for family in families)

        for family in families:
            if family is not None and not font_manager.font_exists(family):
                print(f"Could not find font '{family}'. Install it, or add it to the fonts folder.")

        return font_manager.FontInfo(families)

    def check_match(self, executable, window_title):
        return re.fullmatch(self.executable, executable) and re.fullmatch(self.window_title, window_title)

    def __repr__(self):
        return f"<Context exe='{self.executable}' title='{self.window_title}' " \
               f"font={repr(self.font_info)} tabsize={self.tabsize}>"


def _get_window():
    platform = sys.platform

    if platform in ("Windows", "win32", "cygwin"):
        return _get_window_windows()
    else:
        raise EnvironmentError(f"Unsupported platform {platform}")


def _get_window_windows():
    hWnd = ctypes.windll.user32.GetForegroundWindow()

    title_length = ctypes.windll.user32.GetWindowTextLengthW(hWnd)
    title = ctypes.create_unicode_buffer(title_length + 1)
    ctypes.windll.user32.GetWindowTextW(hWnd, title, title_length + 1)

    pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hWnd, ctypes.pointer(pid))

    hProcess = ctypes.windll.kernel32.OpenProcess(0x0401, False, pid)
    executable_path = ctypes.create_unicode_buffer(512)
    ctypes.windll.psapi.GetProcessImageFileNameW(hProcess, executable_path, 512)

    executable = os.path.basename(executable_path.value)
    return executable, title.value


def get_context():
    executable, window_title = _get_window()

    for c in contexts:
        if c.check_match(executable, window_title):
            return c

    return default_context


# ----- Main ----- #
parser = configparser.ConfigParser()
parser.read("./contexts.ini", encoding="utf-8")

default_entry = dict(parser["DEFAULT"])
default_context = Context(None, None, default_entry)

contexts = []
for key, entry in dict(parser).items():
    if key == "DEFAULT":
        continue

    executable, window_title = re.fullmatch(r"((?:[^\\|]|\\.)+)\|((?:[^\\|]|\\.)+)", key).groups()
    entry = default_entry | dict(entry)
    contexts.append(Context(executable, window_title, entry))

contexts = tuple(contexts)
