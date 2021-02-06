import csv
import re
import threading
import time

import config
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
        prefix = config.config["Formatting Controls"]["prefix"]
        return fr"{prefix}l[{name}]"

    return before + _templates[name]


def _substitute_latex(match):
    if type(match) is re.Match:
        before, content, after = match.groups()
        content = content.replace("\\$", "$")
        content += after
    elif type(match) is str:
        before, content = "", match
    else:
        raise TypeError(f"Cannot perform latex substitution on type {type(match)}")

    try:
        parsed = latex_parser.parse(content, _context)
    except latex_parser.Tokenizer.TokenizationError as e:
        print(e)
        parsed = content
    except latex_parser.Tokenizer.BuildError as e:
        print(e)
        parsed = content

    if len(parsed.split("\n")) > 1:
        return before + "\n" + parsed + "\n"

    return parsed


def reformat(original):
    global _context
    global _templates

    _context = context_manager.get_context()
    print(original, _context)

    prefix = config.config["Formatting Controls"]["prefix"]
    escaped_prefix = re.escape(prefix)

    latex_by_default = int(config.config["Formatting Controls"]["latex_by_default"])
    if original == f"{prefix}lt":
        if _templates:
            return "All templates: " + ", ".join(name for name in _templates)
        return "No templates"

    if match := re.fullmatch(fr"^{escaped_prefix}s\[([\w\d\s]+?)] ?([\w\W]+)", original):
        name, template = match.groups()
        _templates[name] = template
        return ""

    if match := re.fullmatch(fr"^{escaped_prefix}d\[([\w\d\s]+?)]", original):
        name = match.group(1)

        if name in _templates:
            del _templates[name]
            return ""

        return fr"\d[{name}]"

    new_lines = []
    for line in original.split("\n"):
        line, num_replaced = re.subn(fr"(?<!\\)((?:\\\\)*){escaped_prefix}l\[([\w\d\s]+?)]", _substitute_templates,
                                     line)

        if num_replaced > 0:
            new_lines.append(line)
            continue

        if line.startswith(f"{prefix}t") or latex_by_default and not line.startswith(f"{prefix}r"):
            if line.startswith(f"{prefix}t"):
                content = line[len(prefix) + 1:]
            else:
                content = line

            new = re.sub(r"(?<!\\)((?:\\\\)*)\$(.*?)(?<!\\)((?:\\\\)*)*\$", r"\1\2\3", content)
            new = _substitute_latex(new)
            new_lines.append(new)
        else:
            if line.startswith(f"{prefix}r"):
                content = line[len(prefix) + 1:]
            else:
                content = line

            new = re.sub(r"(?<!\\)((?:\\\\)*)\$(.*?)(?<!\\)((?:\\\\)*)*\$", _substitute_latex, content)
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
