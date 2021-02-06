import collections
import re

import components
import config


class Tokenizer:
    def __int__(self):
        pass

    class Token:
        def __repr__(self):
            return "<>"

        def get_id(self):
            return "T"

        def get_component(self):
            return components.Component()

    class BasicToken(Token):
        def __init__(self, text, skip_parsing=False):
            super().__init__()
            self.text = text
            self.skip_parsing = skip_parsing

        def get_id(self):
            return "T-BT"

        def get_component(self):
            return components.TextComponent(self.text)

        def __repr__(self):
            return "<'{}'>".format(self.text)

    class TokenContainer(Token):
        def apply_token_function(self, func):
            pass

    class TokenGroup(TokenContainer):
        def __init__(self, tokens):
            super().__init__()
            self.tokens = tokens

        def apply_token_function(self, func):
            self.tokens = func(self.tokens)

        def get_id(self):
            return "T-TC-TG"

        def get_component(self):
            container = components.ComponentContainer()
            for token in self.tokens:
                container.add_component(token.get_component())

            return container

        def __repr__(self):
            return "<TG [{}]>".format(", ".join(map(repr, self.tokens)))

    class BracketGroup(TokenGroup):
        def __init__(self, opening_char, tokens):
            super().__init__(tokens)
            self.opening_char = opening_char

        def get_id(self):
            return "T-TC-TG-BG-" + self.opening_char

        def get_component(self):
            args = components.bracket_group_arguments[self.opening_char]
            container = components.FlexibleGroup(*args)

            for token in self.tokens:
                container.add_component(token.get_component())

            return container

        def __repr__(self):
            return "<BG '{}' [{}]>".format(self.opening_char, ", ".join(map(repr, self.tokens)))

    class ScriptGroup(TokenContainer):
        def __init__(self, base):
            super().__init__()
            self.base = collections.deque()
            self.base.append(base)
            self.subscript = collections.deque()
            self.superscript = collections.deque()

        def apply_token_function(self, func):
            self.base = func(self.base)
            self.subscript = func(self.subscript)
            self.superscript = func(self.superscript)

        def get_id(self):
            return "T-TC-TG-SG"

        def get_component(self):
            container = components.ComponentContainer()

            base = components.ComponentContainer()
            for token in self.base:
                base.add_component(token.get_component())

            subscript = components.ComponentContainer()
            for token in self.subscript:
                subscript.add_component(token.get_component())

            superscript = components.ComponentContainer()
            for token in self.superscript:
                superscript.add_component(token.get_component())

            container.add_component(base)
            container.add_component(components.ScriptGroup(subscript, superscript))
            return container

        def __repr__(self):
            return "<SG {} [{}] [{}]>".format(repr(self.base), ", ".join(map(repr, self.subscript)),
                                              ", ".join(map(repr, self.superscript)))

    class FunctionGroup(TokenContainer):
        def __init__(self, name, component_class, groups, arguments):
            super().__init__()
            self.name = name
            self.component_class = component_class
            self.groups = groups
            self.arguments = arguments

        def apply_token_function(self, func):
            for group in self.groups:
                group.apply_token_function(func)

        def get_id(self):
            return "T-TC-F-" + self.name

        def get_component(self):
            group_components = (group.get_component() for group in self.groups)
            return self.component_class(*group_components, *self.arguments)

        def __repr__(self):
            return "<F-{} [{}]>".format(self.name, ", ".join(map(repr, self.groups)))

    class TokenizationError(BaseException):
        pass

    class BuildError(BaseException):
        pass

    @staticmethod
    def tokenize(source, show_steps=False):
        def show_step(*args):
            if show_steps:
                print(*args)

        show_step(0, source)
        tokens = Tokenizer._partially_tokenize(source)
        show_step(1, tokens)
        tokens = Tokenizer._group_tokens(tokens)
        show_step(2, tokens)
        tokens = Tokenizer._parse_scripts(tokens)
        show_step(3, tokens)
        tokens = Tokenizer._parse_functions(tokens)
        show_step(4, tokens)
        tokens = Tokenizer._parse_shortcuts(tokens)
        show_step(5, tokens)
        tokens = Tokenizer._add_spacing(tokens)
        show_step(6, tokens)
        tokens = Tokenizer._compress_tokens(tokens)
        show_step(7, tokens)
        token_group = Tokenizer.TokenGroup(tokens)
        show_step(8, token_group)
        return token_group

    @staticmethod
    def _partially_tokenize(source):
        # source = re.sub(r"[]", "", source)
        # ([\\(){}\[\]|+\-*×÷^_]|[a-zA-Z]+|\d[a-zA-Z\d]*)
        # ([a-zA-Z]+|\d[a-zA-Z\d]*|.)
        tokens = re.split(r"([a-zA-Z]+|\d+|.)", source)
        tokens = filter(lambda x: x.replace(" ", ""), tokens)
        tokens = (Tokenizer.BasicToken(token) for token in tokens)
        return collections.deque(tokens)

    @staticmethod
    def _group_tokens(tokens):
        pairs = {"{": "}", "(": ")", "[": "]", "|": "|"}

        depth = 0
        group_flag = False
        opening, closing = None, None
        escape_state = None

        grouped_tokens = collections.deque()
        dump = []

        for basic_token in tokens:
            token_text = basic_token.text

            if escape_state is None and token_text == "\\":
                escape_state = "\\"
                continue

            if escape_state == "\\" and token_text == "left" or token_text == "right":
                escape_state = basic_token.text
                continue

            if escape_state == "\\" and token_text == "\\":
                dump.append(Tokenizer.BasicToken("\\\\"))
                escape_state = None
                continue

            if not group_flag and opening is None and token_text == "{" and escape_state is None:
                grouped_tokens.extend(dump)
                dump = []
                group_flag = True
                depth = 1
                continue

            if not group_flag and opening is None and token_text in pairs:
                grouped_tokens.extend(dump)
                dump = []
                opening = token_text
                closing = pairs[opening]
                depth = 1
                escape_state = None
                continue

            if group_flag and token_text == "{" and escape_state is None:
                depth += 1
            elif group_flag and token_text == "}" and escape_state is None:
                depth -= 1

            elif token_text == opening == closing:
                if escape_state == "left":
                    depth += 1
                elif escape_state == "right":
                    depth -= 1
                elif depth == 0:
                    depth += 1
                else:
                    depth -= 1

            elif token_text == opening:
                depth += 1
            elif token_text == closing:
                depth -= 1

            if group_flag and depth == 0:
                grouped_tokens.append(Tokenizer.TokenGroup(Tokenizer._group_tokens(dump)))
                group_flag = False
                dump = []
            elif token_text == closing and depth == 0:
                grouped_tokens.append(Tokenizer.BracketGroup(opening, Tokenizer._group_tokens(dump)))
                opening = None
                closing = None
                dump = []
            elif escape_state == "\\":
                dump.append(Tokenizer.BasicToken(Tokenizer._replace_symbol("\\" + token_text)))
            elif escape_state == "left" or escape_state == "right":
                dump.append(Tokenizer.BasicToken("\\" + escape_state))
                dump.append(basic_token)
            else:
                dump.append(basic_token)

            escape_state = None

        if depth != 0:
            raise Tokenizer.TokenizationError("Imbalanced Brackets")

        if escape_state is not None:
            print("Warn: Trailing '\\, '\\left' or '\\right' within group")

        grouped_tokens.extend(dump)
        return grouped_tokens

    @staticmethod
    def _replace_symbol(token_text):
        if token_text.startswith("\\") and (key := token_text[1:]) in symbols:
            return symbols[key]
        return token_text

    @staticmethod
    def _fetch_tokens(tokens, target_types):
        fetched = []

        try:
            for target_type in target_types:
                next_token = tokens.popleft()

                if not target_type or next_token.get_id().startswith(target_type):
                    fetched.append(next_token)
                else:
                    raise Tokenizer.BuildError("Token {} is not of type {}".format(next_token, target_type))

        except IndexError:
            raise Tokenizer.BuildError("No tokens could be fetched".format(target_type))

        return tokens, fetched

    @staticmethod
    def _parse_scripts(tokens):
        parsed_tokens = collections.deque()

        while len(tokens) > 0:
            token = tokens.popleft()

            if isinstance(token, Tokenizer.TokenContainer):
                token.apply_token_function(Tokenizer._parse_scripts)
                parsed_tokens.append(token)
                continue

            if token.text == "_":
                script_flag = 1
            elif token.text == "^":
                script_flag = 2
            else:
                script_flag = 0

            if script_flag:
                if len(parsed_tokens) > 0:
                    base = parsed_tokens.pop()
                else:
                    base = Tokenizer.BasicToken("")

                if type(base) is Tokenizer.ScriptGroup:
                    if script_flag == 1 and len(base.subscript) == 0 or script_flag == 2 and len(base.superscript) == 0:
                        tokens, (script,) = Tokenizer._fetch_tokens(tokens, ("",))

                        if script_flag == 1:
                            base.subscript.append(script)
                        else:
                            base.superscript.append(script)

                        parsed_tokens.append(base)
                        continue
                    elif script_flag == 1:
                        raise Tokenizer.TokenizationError("Multiple subscripts found inline")
                    else:
                        raise Tokenizer.TokenizationError("Multiple superscripts found inline")

                tokens, (script,) = Tokenizer._fetch_tokens(tokens, ("",))
                group = Tokenizer.ScriptGroup(base)

                if isinstance(script, Tokenizer.TokenGroup):
                    script.apply_token_function(Tokenizer._parse_scripts)

                elif script_flag == 1 and script.text == "_":
                    raise Tokenizer.TokenizationError("Multiple subscripts found inline")
                elif script_flag == 2 and script.text == "^":
                    raise Tokenizer.TokenizationError("Multiple superscripts found inline")

                if script_flag == 1:
                    group.subscript.append(script)
                else:
                    group.superscript.append(script)

                parsed_tokens.append(group)
                continue

            parsed_tokens.append(token)

        return parsed_tokens

    @staticmethod
    def _parse_functions(tokens):
        parsed_tokens = collections.deque()

        while len(tokens) > 0:
            token = tokens.popleft()

            if isinstance(token, Tokenizer.TokenContainer):
                token.apply_token_function(Tokenizer._parse_functions)
                parsed_tokens.append(token)
                continue

            if type(token) is not Tokenizer.BasicToken:
                raise Tokenizer.TokenizationError("Unexpected token type '{}'".format(token.get_id()))

            if not token.text.startswith("\\"):
                parsed_tokens.append(token)
                continue

            name = token.text[1:]
            if name == "left" or name == "right":
                continue

            if name in simple_functions:
                next_token = tokens[0]
                if type(next_token) is not Tokenizer.TokenGroup:
                    print("Encountered simple function '{}' but no following group. Treating as text".format(name))
                    token.text = name
                    token.skip_parsing = True
                    parsed_tokens.append(token)
                    continue

                if len(next_token.tokens) != 1 or type(contents := next_token.tokens[0]) is not Tokenizer.BasicToken:
                    print("Encountered simple function '{}' but following group was not valid. Treating as text"
                          .format(name))
                    token.text = name
                    token.skip_parsing = True
                    parsed_tokens.append(token)
                    continue

                if contents.text not in simple_functions[name]:
                    print("The simple function '{}' has no defined output for the input '{}'. Treating as text"
                          .format(name, contents.text))
                    token.text = name
                    token.skip_parsing = True
                    parsed_tokens.append(token)
                    continue

                tokens.popleft()

                token.text = simple_functions[name][contents.text]
                token.skip_parsing = True
                parsed_tokens.append(token)
                continue

            elif name not in components.function_components:
                print("Encountered unknown function '{}'. Treating as text".format(name))
                token.text = name
                token.skip_parsing = True
                parsed_tokens.append(token)
                continue

            component_class, num_groups, arguments = components.function_components[name]
            tokens, groups = tuple(Tokenizer._fetch_tokens(tokens, tuple("T-TC-TG" for _ in range(num_groups))))
            for group in groups:
                group.apply_token_function(Tokenizer._parse_functions)

            function_group = Tokenizer.FunctionGroup(name, component_class, groups, arguments)
            parsed_tokens.append(function_group)

        return parsed_tokens

    @staticmethod
    def _parse_shortcuts(tokens):
        parsed_tokens = collections.deque()
        allow_fraction_shortcut = int(config.config["Parser"]["allow_fraction_shortcut"])

        fraction_class, _, fraction_arguments = components.function_components["frac"]

        while len(tokens) > 0:
            token = tokens.popleft()

            if isinstance(token, Tokenizer.TokenContainer):
                token.apply_token_function(Tokenizer._parse_shortcuts)
                parsed_tokens.append(token)
                continue

            if token.skip_parsing:
                parsed_tokens.append(token)
                continue

            if type(token) is not Tokenizer.BasicToken:
                parsed_tokens.append(token)
                continue

            if allow_fraction_shortcut and token.text == "/" and len(parsed_tokens) > 0 and len(tokens) > 0:
                top = parsed_tokens.pop()
                bottom = tokens.popleft()

                if type(top) is Tokenizer.BasicToken:
                    top_tokens = collections.deque()
                    top_tokens.append(top)
                    top = Tokenizer.TokenGroup(top_tokens)

                if type(bottom) is Tokenizer.BasicToken:
                    bottom_tokens = collections.deque()
                    bottom_tokens.append(bottom)
                    bottom = Tokenizer.TokenGroup(bottom_tokens)

                function_group = Tokenizer.FunctionGroup("frac", fraction_class, (top, bottom), fraction_arguments)
                parsed_tokens.append(function_group)
                continue

            parsed_tokens.append(token)

        return parsed_tokens

    @staticmethod
    def _add_spacing(tokens):
        if len(tokens) == 0:
            return collections.deque()

        formatted_tokens = collections.deque()

        if len(tokens) == 1 and isinstance(tokens[0], Tokenizer.TokenContainer):
            token = tokens.popleft()
            token.apply_token_function(Tokenizer._add_spacing)
            formatted_tokens.append(token)
            return formatted_tokens
        elif len(tokens) == 1:
            formatted_tokens.append(tokens.popleft())
            return formatted_tokens

        token = tokens.popleft()
        unary_flag = False

        while len(tokens) > 0:
            last_token = token
            token = tokens.popleft()

            if isinstance(last_token, Tokenizer.TokenContainer):
                last_token.apply_token_function(Tokenizer._add_spacing)
                formatted_tokens.append(last_token)

                if type(last_token) is not Tokenizer.ScriptGroup or type(token) is not Tokenizer.ScriptGroup:
                    if type(token) is Tokenizer.BasicToken and token.text in non_spaced_chars:
                        continue
                    formatted_tokens.append(Tokenizer.BasicToken(" "))
                continue

            if type(last_token) is not Tokenizer.BasicToken or type(token) is not Tokenizer.BasicToken:
                formatted_tokens.append(last_token)

                if type(last_token) is Tokenizer.BasicToken and last_token.text in non_spaced_chars \
                        and (type(token) is Tokenizer.BracketGroup and token.opening_char != "{"
                             or type(token) is Tokenizer.ScriptGroup):
                    continue

                formatted_tokens.append(Tokenizer.BasicToken(" "))
                continue

            formatted_tokens.append(last_token)

            if unary_flag:
                unary_flag = False
            elif last_token.text in equality_operator_chars and token.text in unary_operator_chars:
                unary_flag = True
                formatted_tokens.append(Tokenizer.BasicToken(" "))
            elif any(char not in non_spaced_chars for char in last_token.text) or token.text not in non_spaced_chars:
                formatted_tokens.append(Tokenizer.BasicToken(" "))

        if isinstance(token, Tokenizer.TokenContainer):
            token.apply_token_function(Tokenizer._add_spacing)

        formatted_tokens.append(token)
        return formatted_tokens

    @staticmethod
    def _compress_tokens(tokens):
        compressed_tokens = collections.deque()

        buffer = []
        for token in tokens:
            if type(token) is not Tokenizer.BasicToken:
                if buffer:
                    text = "".join(buffer)
                    compressed_tokens.append(Tokenizer.BasicToken(text))
                    buffer = []

                if isinstance(token, Tokenizer.TokenContainer):
                    token.apply_token_function(Tokenizer._compress_tokens)

                compressed_tokens.append(token)
                continue

            buffer.append(token.text)

        if buffer:
            text = "".join(buffer)
            compressed_tokens.append(Tokenizer.BasicToken(text))

        return compressed_tokens


def parse(text, context):
    show_steps = bool(int(config.config["Parser"]["show_steps"]))
    token = Tokenizer.tokenize(text, show_steps)
    return token.get_component().render(context)


# ----- Main ----- #
symbols = {}

with open("symbols/symbols.txt", encoding="utf-8") as file:
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            x, y = line.strip().split(" ")
            symbols[x] = y

with open("symbols/spacing_chars.txt", encoding="utf-8") as file:
    non_spaced_chars = set(file.readline().strip())
    equality_operator_chars = set(file.readline().strip())
    unary_operator_chars = set(file.readline().strip())

variable_chars = {}
with open("symbols/variables.txt", encoding="utf-8") as file:
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            x, y = line.strip().split(" ")
            variable_chars[x] = y

simple_functions = {}
with open("symbols/simple_functions.txt", encoding="utf-8") as file:
    for line in file.readlines():
        if line.strip() and not line.strip().startswith("#"):
            x, y, z = line.strip().split(" ")
            if x not in simple_functions:
                simple_functions[x] = {}
            simple_functions[x][y] = z
