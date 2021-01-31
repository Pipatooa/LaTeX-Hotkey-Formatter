import csv
import re
import threading
import time

import context_manager
import latex_parser

_context = None


def _template_saver():
    global _saved_templates

    while True:
        time.sleep(1)

        if _saved_templates != _templates:
            _save_templates(_templates)
            _saved_templates = _templates.copy()


def _save_templates(templates):
    global _saved_templates

    with open("./templates.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("Name", "Template"))
        writer.writerows(templates.items())

    _saved_templates = templates


def _substitute_templates(match):
    before, name = match.groups()

    if name not in _templates:
        return fr"{before}\l[{name}]"

    return before + _templates[name]


def _substitute_latex(match):
    if type(match) is re.Match:
        before, content = match.groups()
        content = content.replace("\\$", "$")
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
    global _templates

    _context = context_manager.get_context()
    print(original, _context)

    if match := re.fullmatch(r"^\\s\[([\w\d\s]+?)] ?([\w\W]+)", original):
        name, template = match.groups()
        _templates[name] = template
        return ""

    if match := re.fullmatch(r"^\\d\[([\w\d\s]+?)]", original):
        name = match.group(1)

        if name in _templates:
            del _templates[name]
            return ""

        return fr"\d[{name}]"

    new_lines = []
    for line in original.split("\n"):
        line, num_replaced = re.subn(r"(^|(?:\\\\|\\?[^\\])+?)\\l\[([\w\d\s]+?)]", _substitute_templates, line)

        if num_replaced > 0:
            new_lines.append(line)
            continue

        if line.startswith(r"\t"):
            content = line[2:]
            new = _substitute_latex(content)
            new_lines.append(new)
        else:
            new = re.sub(r"((?:[^\\$]|\\.)*)\$((?:[^\\$]|\\.)*)\$", _substitute_latex, line)
            new_lines.extend(new.split("\n"))

    return "\n".join(new_lines).lstrip("\n").rstrip()


# ----- Main ----- #
_templates = {}
_saved_templates = {}

with open("./templates.csv", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for name, template in reader:
        _templates[name] = template
        _saved_templates[name] = template

t = threading.Thread(target=_template_saver)
t.start()
