import itertools
import math


class BuildContext:
    def __init__(self, context):
        self.context = context
        self.baseline = 0
        self.height = 1

    def new(self):
        return BuildContext(self.context)

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

    def render(self, context):
        return "\n".join(line.render(context) for line in reversed(self.lines))


class Line:
    def __init__(self, pos=None, text=None):
        if pos is not None:
            self.items = [(pos, text)]
        else:
            self.items = []

    def shift(self, offset):
        self.items = [(pos + offset, text) for pos, text in self.items]

    def render(self, context):
        partial = []

        self.items.sort()

        tab_width = context.tabsize * context.font.space_width
        last_pos = 0

        for pos, text in self.items:
            delta = pos - last_pos

            num_tabs = math.floor(delta / tab_width)
            delta -= num_tabs * tab_width
            last_pos += num_tabs * tab_width

            num_spaces = math.floor(delta / context.font.space_width)
            last_pos += num_spaces * context.font.space_width

            new = "\t" * num_tabs + " " * num_spaces + text
            last_pos += context.font.get_text_width(text)

            partial.append(new)

        return "".join(partial).rstrip(" ")

    def get_raw(self):
        return "".join(x[2] for x in self.items)

    def __add__(self, other):
        new = Line()
        new.items = self.items + other.items
        return new

    def __repr__(self):
        return "<Line: " + ", ".join("{:.2f}: {}".format(pos, text) for pos, text in self.items) + ">"


class Component:
    def build(self, build_context):
        return BuiltComponent(0, 0, [], 0, "inline")

    def render(self, context):
        build_context = BuildContext(context)
        return self.build(build_context).render(context)


class TextComponent(Component):
    def __init__(self, text):
        super().__init__()
        self.text = list(reversed(text.split("\n")))

    @staticmethod
    def _center(font, text, width):
        pos = max(0, width - font.get_text_width(text)) / 2
        return pos, text

    def build(self, build_context):
        width = max(build_context.context.font.get_text_width(line) for line in self.text)
        height = len(self.text)

        lines = [Line(*TextComponent._center(build_context.context.font, line, width)) for line in self.text]
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
    def __init__(self, top, bottom, div_char_simple, div_char_complex, overfill):
        super().__init__()
        self.top = top
        self.bottom = bottom

        self.div_char_simple = div_char_simple
        self.div_char_complex = div_char_complex
        self.overfill = overfill

    def _build_simple(self, top_simplified, bottom_simplified, build_context):
        raw_line = top_simplified + self.div_char_simple + bottom_simplified

        width = build_context.context.font.get_text_width(raw_line)
        lines = [Line(0, raw_line)]

        return BuiltComponent(width, 1, lines, 0, "inline")

    def _build_complex(self, build_context):
        top_built = self.top.build(build_context.new())
        bottom_built = self.bottom.build(build_context.new())

        div_char_width = build_context.context.font.get_text_width(self.div_char_complex)
        divider = self.div_char_complex * (
                    math.ceil(max(top_built.width, bottom_built.width) / div_char_width) + self.overfill)

        width = build_context.context.font.get_text_width(divider)
        baseline = len(bottom_built.lines)

        top_delta = (width - top_built.width) / 2
        bottom_delta = (width - bottom_built.width) / 2

        for line in top_built.lines:
            line.shift(top_delta)

        for line in bottom_built.lines:
            line.shift(bottom_delta)

        lines = bottom_built.lines + [Line(0, divider)] + top_built.lines

        return BuiltComponent(width, len(lines), lines, baseline, "inline")

    def build(self, build_context):
        top_simple, top_simplified = ScriptGroup.simplify_superscript(self.top)
        bottom_simple, bottom_simplified = ScriptGroup.simplify_subscript(self.bottom)

        if top_simple and bottom_simple:
            return self._build_simple(top_simplified, bottom_simplified, build_context)

        return self._build_complex(build_context)


class FlexChars:
    def __init__(self, single, double_top, double_bottom, top, top_mid, mid, bottom_mid, bottom, filler):
        self.single = single

        self.double_top = double_top
        self.double_bottom = double_bottom

        self.top = top
        self.top_mid = top_mid
        self.mid = mid
        self.bottom_mid = bottom_mid
        self.bottom = bottom

        self.filler = filler

    def get_chars(self, length):
        if length == 1:
            yield self.single
            return

        elif length == 2:
            yield self.double_top
            yield self.double_bottom

        elif length % 2 == 1:
            yield self.bottom
            yield from (self.filler for _ in range((length - 3) // 2))
            yield self.mid
            yield from (self.filler for _ in range((length - 3) // 2))
            yield self.top

        else:
            yield self.bottom
            yield from (self.filler for _ in range((length - 4) // 2))
            yield self.bottom_mid
            yield self.top_mid
            yield from (self.filler for _ in range((length - 4) // 2))
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

        left_width = max(build_context.context.font.get_text_width(char) for char in left_chars)
        right_width = max(build_context.context.font.get_text_width(char) for char in right_chars)

        new_lines = []
        for start_char, line, end_char in zip(left_chars, built.lines, right_chars):
            line.shift(left_width)
            new_lines.append(Line(0, start_char) + line + Line(built.width + left_width, end_char))

        built.lines = new_lines
        built.width += left_width + right_width

        return built


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
    def _simplify(component, char_set):
        if type(component) is ComponentContainer:
            simplified_components = []
            for c in component.components:
                simple, simplified = ScriptGroup._simplify(c, char_set)

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

    @staticmethod
    def simplify_superscript(component):
        return ScriptGroup._simplify(component, ScriptGroup._superscript_chars)

    @staticmethod
    def simplify_subscript(component):
        return ScriptGroup._simplify(component, ScriptGroup._subscript_chars)

    def build(self, build_context):
        bottom_simple, bottom_simplified = ScriptGroup.simplify_subscript(self.subscript)
        if bottom_simple:
            subscript = TextComponent(bottom_simplified).build(build_context.new())
        else:
            subscript = self.subscript.build(build_context.new())

        top_simple, top_simplified = ScriptGroup.simplify_superscript(self.superscript)
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


# ------ Main ----- #
bracket_group_arguments = {
    "(": (FlexChars(*"⎧⎧⎩⎧⎪⎪⎪⎩⎪"), FlexChars(*"⎫⎫⎭⎫⎪⎪⎪⎭⎪")),
    "{": (FlexChars(*"{⎰⎱⎧⎭⎨⎫⎩⎢"), FlexChars(*"}⎱⎰⎫⎩⎬⎧⎭⎪")),
    "[": (FlexChars(*"[⎡⎣⎡⎢⎢⎢⎣⎢"), FlexChars(*"]⎤⎦⎤⎢⎢⎢⎦⎢")),
    "|": (FlexChars(*"⎢⎢⎢⎢⎢⎢⎢⎢⎢"), FlexChars(*"⎢⎢⎢⎢⎢⎢⎢⎢⎢"))
}

function_components = {
    "frac": (Fraction, 2, ("⁄", "—", 1))
}
