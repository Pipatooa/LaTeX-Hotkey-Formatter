import re


# Returns pattern from regex file
def get_pattern(line):
    line = line.strip().replace("EMPTYSTR", "")

    pattern, sub = line.split(" ")
    pattern = pattern.replace("SPACE", " ")
    sub = sub.replace("SPACE", " ")

    return re.compile(pattern), sub


# Read regex files
with open("symbols/symbols.regex", "r", encoding="utf-8") as file:
    constants_regex = []
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            constants_regex.append(get_pattern(line))

with open("symbols/scripts.txt", "r", encoding="utf-8") as file:
    scripts = []
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            scripts.append(tuple(line.strip().split()))

with open("symbols/formatting.regex", "r", encoding="utf-8") as file:
    formatting_regex = []
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            formatting_regex.append(get_pattern(line))


def replace_symbols(content):
    for pattern, sub in constants_regex:
        content = pattern.sub(sub, content)

    return content


def replace_superscript(match):
    if type(match) is re.Match:
        if not (new := match.group(1)):
            new = match.group(2)
    else:
        new = match

    for old_char, _, new_char in scripts:
        new = new.replace(old_char, new_char)
    return new


def replace_subscript(match):
    if type(match) is re.Match:
        if not (new := match.group(1)):
            new = match.group(2)
    else:
        new = match

    for old_char, new_char, _ in scripts:
        new = new.replace(old_char, new_char)
    return new


def replace_ffraction(match):
    if match.group(1):
        a, b = match.group(1, 2)
    else:
        a, b = match.group(3, 4)

    a = replace_superscript(a)
    b = replace_subscript(b)

    new = "{}⁄{}".format(a, b)
    return new


def replace_fraction(match):
    a, b = match.groups()

    a_width = max(len(x) for x in a.split("\n"))
    b_width = max(len(x) for x in b.split("\n"))
    max_width = max(a_width, b_width)

    a = a._center(max_width, )
    b = b._center(max_width, )
    divider = "⎯" * max_width

    new = "\\ccstartfrac{}\\ccmidfrac{}\\ccmidfrac{}\\ccendfrac".format(a, divider, b)
    return new


def format_fractions(content):
    new = []

    for line in content.split("\n"):
        if "\\ccstartfrac" not in line:
            new.append(line)
            continue

        upper, mid, lower = [], [], []
        for section in re.split(r"\\ccstartfrac|\\ccendfrac", line):
            if "\\ccmidfrac" in section:
                top, div, bottom = section.split("\\ccmidfrac")
                upper += top
                mid += div
                lower += bottom
            else:
                upper.append(" " * len(section))
                mid.append(section)
                lower.append(" " * len(section))

        new.append("".join(upper))
        new.append("".join(mid))
        new.append("".join(lower))

    return "\n".join(new)


def replace_formatting(content):
    for pattern, sub in formatting_regex:
        content = pattern.sub(sub, content)

    return content


def parse(original):
    new = original.replace("\r", "")

    # Replace recognised symbols
    new = replace_symbols(new)

    # Superscript & Subscript
    new = re.sub(r"\^(?:{(.+?)}|(-?\d+|.))", replace_superscript, new)
    new = re.sub(r"_(?:{(.+?)}|(-?\d+|.))", replace_subscript, new)

    # Formatting corrections
    new = replace_formatting(new)

    # Fractions
    new = re.sub(r"\\ffrac\{(.+?)}\{(.+?)}|(\d+x?)/(\d+|x)", replace_ffraction, new)
    new = re.sub(r"\\frac\{(.+?)}\{(.+?)}", replace_fraction, new)
    new = format_fractions(new)

    return new
