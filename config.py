import configparser

# ----- Main ----- #
_parser = configparser.ConfigParser()
_parser.read("./config.ini", encoding="utf-8")

config = {section: dict(contents) for section, contents in dict(_parser).items() if section != "DEFAULT"}
