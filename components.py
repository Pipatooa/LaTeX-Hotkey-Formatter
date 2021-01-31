import itertools
import math


class BuildContext:
    def __init__(self, font):
        self.font = font
        self.baseline = 0
        self.height = 1

    def new(self):
        return BuildContext(self.font)

    def update(self, built_component):
        self.baseline = built_component.baseline
        self.height = built_component.height


class BuiltComponent:
    def __init__(self, width, height, lines, baseline, alignment):
        self.width = width
        self.height = height
        self.lines = lines

        self.baseline = baseline
        self.alignment = alignment

    def v_resize(self, height, offset):
        self.lines = [Line() for _ in range(offset)] + self.lines + \
                     [Line() for _ in range(height - self.height - offset)]
        self.height = height

    def get_delta(self, other):
        if self.alignment == "bottom":
            return -1 - self.baseline
        if self.alignment == "inline":
            return other.baseline - self.baseline
        if self.alignment == "top":
            return other.height - self.baseline
        return None

    def make_similar(self, other):
        height_delta = other.get_delta(self)
        height_delta_a = max(0, -height_delta)
        height_delta_b = max(0, height_delta)

        new_height = max(self.height + height_delta_a, other.height + height_delta_b)

        if self.height != new_height:
            self.v_resize(new_height, height_delta_a)

        if other.height != new_height:
            other.v_resize(new_height, height_delta_b)

        self.baseline += height_delta_a

    def combine(self, other):
        self.make_similar(other)

        for line in other.lines:
            line.shift(self.width)

        self.lines = [a + b for a, b in zip(self.lines, other.lines)]
        self.width += other.width

    def render(self, font):
        return "\n".join(line.render(font) for line in reversed(self.lines))


class Line:
    def __init__(self, pos=None, text=None):
        if pos is not None:
            self.items = [(pos, text)]
        else:
            self.items = []

    def shift(self, offset):
        self.items = [(pos + offset, text) for pos, text in self.items]

    def render(self, font):
        partial = []

        self.items.sort()

        last_pos = 0
        for pos, text in self.items:
            delta = pos - last_pos
            new = " " * math.floor(delta / font.space_width) + text

            partial.append(new)
            last_pos += font.get_text_width(new)

        return "".join(partial)

    def get_raw(self):
        return "".join(x[2] for x in self.items)

    def __add__(self, other):
        new = Line()
        new.items = self.items + other.items
        return new

    def __repr__(self):
        return "<Line: " + ", ".join("{:.2f}: {}".format(pos, text) for pos, text in self.items) + ">"


class Component:
    def __init__(self):
        pass

    def build(self, build_context):
        return BuiltComponent(0, 0, [], 0, "inline")

    def render(self, font):
        build_context = BuildContext(font)
        return self.build(build_context).render(font)


class TextComponent(Component):
    def __init__(self, text):
        super().__init__()
        self.text = list(reversed(text.split("\n")))

    @staticmethod
    def _center(font, text, width):
        pos = max(0, width - font.get_text_width(text)) / 2
        return pos, text

    def build(self, build_context):
        width = max(build_context.font.get_text_width(line) for line in self.text)
        height = len(self.text)

        lines = [Line(*TextComponent._center(build_context.font, line, width)) for line in self.text]
        baseline = math.ceil(height / 2) - 1

        return BuiltComponent(width, height, lines, baseline, "inline")


class ComponentContainer(Component):
    def __init__(self):
        super().__init__()
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def add_components(self, components):
        self.components.extend(components)

    def build(self, build_context):
        if len(self.components) == 0:
            return BuiltComponent(0, 1, [], 0, "inline")

        new_context = build_context.new()
        built = self.components[0].build(new_context)
        new_context.update(built)

        for c in itertools.islice(self.components, 1, len(self.components)):
            built.combine(c.build(new_context))
            new_context.update(built)

        return built


class Fraction(Component):
    def __init__(self, top, bottom, div_char, overfill):
        super().__init__()
        self.top = top
        self.bottom = bottom

        self.div_char = div_char
        self.overfill = overfill

    def build(self, build_context):
        top_built = self.top.build(build_context.new())
        bottom_built = self.bottom.build(build_context.new())

        div_char_width = build_context.font.get_text_width(self.div_char)
        divider = self.div_char * (math.ceil(max(top_built.width, bottom_built.width) / div_char_width) + self.overfill)

        width = build_context.font.get_text_width(divider)
        baseline = len(bottom_built.lines)

        top_delta = (width - top_built.width) / 2
        bottom_delta = (width - bottom_built.width) / 2

        for line in top_built.lines:
            line.shift(top_delta)

        for line in bottom_built.lines:
            line.shift(bottom_delta)

        lines = bottom_built.lines + [Line(0, divider)] + top_built.lines

        return BuiltComponent(width, len(lines), lines, baseline, "inline")


class FlexChars:
    def __init__(self, top, mid, bottom, top_double, bottom_double, single):
        self.top = top
        self.mid = mid
        self.bottom = bottom

        self.top_double = top_double
        self.bottom_double = bottom_double

        self.single = single

    def get_chars(self, length):
        if length == 1:
            yield self.single
            return

        elif length == 2:
            yield self.bottom_double
            yield self.top_double

        else:
            yield self.bottom
            yield from (self.mid for _ in range(length - 2))
            yield self.top


class FlexibleGroup(ComponentContainer):
    def __init__(self, left_chars, right_chars):
        super().__init__()
        self.left_chars = left_chars
        self.right_chars = right_chars

    def build(self, build_context):
        built = super().build(build_context.new())

        left_chars = list(self.left_chars.get_chars(built.height))
        right_chars = list(self.right_chars.get_chars(built.height))

        left_width = max(build_context.font.get_text_width(char) for char in left_chars)
        right_width = max(build_context.font.get_text_width(char) for char in right_chars)

        new_lines = []
        for start_char, line, end_char in zip(left_chars, built.lines, right_chars):
            line.shift(left_width)
            new_lines.append(Line(0, start_char) + line + Line(built.width + left_width, end_char))

        built.lines = new_lines
        built.width += left_width + right_width

        return built


class RoundBracketGroup(FlexibleGroup):
    left_chars = FlexChars("⎧", "⎪", "⎩", "⎧", "⎩", "(")
    right_chars = FlexChars("⎫", "⎪", "⎭", "⎫", "⎭", ")")

    def __init__(self):
        super().__init__(RoundBracketGroup.left_chars, RoundBracketGroup.right_chars)


class CurlyBracketGroup(FlexibleGroup):
    left_chars = FlexChars("⎧", "⎨", "⎩", "⎰", "⎱", "{")
    right_chars = FlexChars("⎫", "⎬", "⎭", "⎱", "⎰", "}")

    def __init__(self):
        super().__init__(CurlyBracketGroup.left_chars, CurlyBracketGroup.right_chars)


class SquareBracketGroup(FlexibleGroup):
    left_chars = FlexChars("⎡", "⎢", "⎣", "⎡", "⎣", "[")
    right_chars = FlexChars("⎤", "⎥", "⎦", "⎤", "⎦", "]")

    def __init__(self):
        super().__init__(SquareBracketGroup.left_chars, SquareBracketGroup.right_chars)


class BarBracketGroup(FlexibleGroup):
    left_chars = FlexChars("⎢", "⎢", "⎢", "⎢", "⎢", "|")
    right_chars = FlexChars("⎢", "⎢", "⎢", "⎢", "⎢", "|")

    def __init__(self):
        super().__init__(BarBracketGroup.left_chars, BarBracketGroup.right_chars)


class ScriptGroup(Component):
    with open("symbols/subscript.txt", encoding="utf-8") as file:
        items = (line.strip().split(" ") for line in file.readlines())
        _subscript_chars = {a: b for a, b in items}

    with open("symbols/superscript.txt", encoding="utf-8") as file:
        items = (line.strip().split(" ") for line in file.readlines())
        _superscript_chars = {a: b for a, b in items}

    def __init__(self, subscript, superscript):
        super().__init__()
        self.subscript = subscript
        self.superscript = superscript

    @staticmethod
    def simplify(component, char_set):
        if type(component) is ComponentContainer:
            simplified_components = []
            for c in component.components:
                simple, simplified = ScriptGroup.simplify(c, char_set)

                if not simple:
                    return False, None

                simplified_components.append(simplified)
            return True, "".join(simplified_components)

        elif type(component) is not TextComponent:
            return False, None

        if len(component.text) != 1:
            return False, None

        simplified_components = []
        for char in component.text[0]:
            if char not in char_set:
                return False, None

            simplified_components.append(char_set[char])
        return True, "".join(simplified_components)

    def build(self, build_context):
        bottom_simple, bottom_simplified = ScriptGroup.simplify(self.subscript, ScriptGroup._subscript_chars)
        if bottom_simple:
            subscript = TextComponent(bottom_simplified).build(build_context.new())
        else:
            subscript = self.subscript.build(build_context.new())

        top_simple, top_simplified = ScriptGroup.simplify(self.superscript, ScriptGroup._superscript_chars)
        if top_simple:
            superscript = TextComponent(top_simplified).build(build_context.new())
        else:
            superscript = self.superscript.build(build_context.new())

        if bottom_simple and top_simple and build_context.height == 1:
            superscript.lines[0].shift(subscript.width)
            new_lines = [subscript.lines[0] + superscript.lines[0]]
            width = subscript.width + superscript.width
            return BuiltComponent(width, 1, new_lines, 0, "inline")

        bottom_lines = subscript.lines
        top_lines = superscript.lines

        if not bottom_simple:
            bottom_lines.append(Line())

        if top_simple:
            top_lines = [Line() for _ in range(build_context.height - 2)] + top_lines
        else:
            top_lines = [Line() for _ in range(build_context.height - 1)] + top_lines

        new_lines = bottom_lines + top_lines

        width = max(subscript.width, superscript.width)
        height = len(new_lines)
        baseline = build_context.baseline + len(bottom_lines) - 1

        return BuiltComponent(width, height, new_lines, baseline, "inline")


class GenericFunction(TextComponent):
    def __init__(self, func_name):
        super().__init__(func_name + " ")


# ------ Main ----- #
bracket_group_components = {
    "(": RoundBracketGroup,
    "{": CurlyBracketGroup,
    "[": SquareBracketGroup,
    "|": BarBracketGroup
}

function_components = {
    "frac": (Fraction, 2, ("—", 1))
}