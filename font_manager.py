import pyglet.font

import config

_dpi = int(config.config["Fonts"]["dpi"])


class FontInfo:
    def __init__(self, families, monospaced=False):
        if not monospaced:
            self.families = families
            self.monospaced = False
            self.font = pyglet.font.load(families, dpi=_dpi)

            self.em = self.font.get_glyphs(" ")[0].height
            self.space_width = self.get_char_width(" ")
        else:
            self.families = None
            self.monospaced = True
            self.font = None

            _font = pyglet.font.load(dpi=_dpi)
            self.em = _font.get_glyphs(" ")[0].height
            self.space_width = self.em

    def get_char_width(self, char):
        if self.monospaced:
            return self.space_width

        print(repr(char), self.font.get_glyphs(char)[0].width)
        return self.font.get_glyphs(char)[0].width

    def get_text_width(self, text):
        if self.monospaced:
            return self.space_width * len(text)

        for char in text:
            print(repr(char), self.get_char_width(char))

        return sum(glyph.width for glyph in self.font.get_glyphs(text))

    def __repr__(self):
        if self.monospaced:
            return "<FontInfo MONOSPACED>"
        return f"<FontInfo families='{self.families}'>"


def font_exists(font_name):
    return pyglet.font.have_font(font_name)


# ----- Main ----- #
pyglet.font.add_directory("./fonts")

locations = config.config["Fonts"]["locations"].split(", ")
for location in locations:
    if location:
        pyglet.font.add_directory(location)
