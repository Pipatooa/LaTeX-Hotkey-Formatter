import re

import context_manager
import latex_parser

_context = None


def _substitute_latex(match):
    if type(match) is re.Match:
        before, content = match.groups()
    elif type(match) is str:
        before, content = "", match
    else:
        raise TypeError(f"Cannot perform latex subsitution on type {type(match)}")

    parsed = latex_parser.parse(content, _context)
    if len(parsed.split("\n")) > 1:
        return before + "\n" + parsed + "\n"

    return before + parsed


def reformat(original):
    global _context
    _context = context_manager.get_context()
    print(original, _context)

    new_lines = []
    for line in original.split("\n"):
        if line.startswith(r"\t"):
            content = line[2:]
            new = _substitute_latex(content)
            new_lines.append(new)
        else:
            new = re.sub(r"((?:[^\\$]|\\.)*)\$((?:[^\\$]|\\.)*)\$", _substitute_latex, line)
            new_lines.extend(new.split("\n"))

    return "\n".join(new_lines).lstrip("\n").rstrip()
