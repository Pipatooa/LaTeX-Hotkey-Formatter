import configparser
import re
import sys
import ctypes
import ctypes.wintypes
import os

from fontTools.ttLib import TTFont
from functools import lru_cache


if sys.platform in ("linux", "linux2"):
    raise NotImplementedError(f"Linux is not currently supported")
elif sys.platform in ("Windows", "win32", "cygwin"):
    pass
else:
    raise EnvironmentError(f"Unknown platform {sys.platform}")


class FontInfo:
    def __init__(self, path=None):
        self.path = path

        if path is not None:
            self.font = TTFont(path)

            self.cmap = self.font["cmap"]
            self.cmap = self.cmap.getcmap(3, 1).cmap

            self.glyph_set = self.font.getGlyphSet()
            self.units_per_em = self.font["head"].unitsPerEm

            self.not_def = self.glyph_set[".notdef"]
            self.space_width = self._get_glyph_width(" ")

    @lru_cache(maxsize=100)
    def _get_glyph_width(self, char):
        if ord(char) in self.cmap and (c := self.cmap[ord(char)]) in self.glyph_set:
            return self.glyph_set[c].width / self.units_per_em
        return self.not_def.width / self.units_per_em

    @lru_cache(maxsize=50)
    def get_text_width(self, text):
        return sum(self._get_glyph_width(char) for char in text)

    def __repr__(self):
        return f"<FontInfo path='{self.path}'>"


class MonoSpacedFont(FontInfo):
    def __init__(self):
        super().__init__()

        self.font = None
        self.space_width = 1

    def _get_glyph_width(self, char):
        return 1

    def get_text_width(self, text):
        return len(text)

    def __repr__(self):
        return f"<MonoSpacedFont>"


class Context:
    def __init__(self, executable, window_title, entry):
        self.executable = executable
        self.window_title = window_title

        self.font = Context._get_font(entry["font"])

    @staticmethod
    def _get_font(path):
        if path == "MONOSPACED":
            return MonoSpacedFont()
        return FontInfo(path)

    def check_match(self, executable, window_title):
        return re.fullmatch(self.executable, executable) and re.fullmatch(self.window_title, window_title)

    def __repr__(self):
        return f"<Context exe='{self.executable}' title='{self.window_title}' font={repr(self.font)}>"


def get_window():
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
    executable, window_title = get_window()

    for c in contexts:
        if c.check_match(executable, window_title):
            return c

    return default_context


# ----- Main ----- #
parser = configparser.ConfigParser()
parser.read("./contexts.ini")

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
