# Latex Hotkey Formatter
LHF is a LaTeX to Unicode parser that is activated by a configurable hotkey. When activated, highlighted text will be reformatted.

### Formatting controls:
Any line of the captured string starting with `\t` will be converted into a unicode representation of the following LaTeX.

### Requirements:
Windows:
```requirements.txt
pynput~=1.7.2
pyperclip~=1.8.1
fonttools~=4.18.2
```

### Config:
#### contexts.ini
```ini
[DEFAULT]
font = MONOSPACED
tabsize = 4

[pycharm64.exe|.*]
font = ./fonts/JetBrainsMono/JetBrainsMono-Light.ttf

[Discord.exe|.*]
font = ./fonts/Whitney/whitneylight.otf

[chrome.exe|Meet - .*]
font = ./fonts/Roboto/Roboto-Regular.ttf
tabsize = 8
```
##### Usage:
The **contexts.ini** file can be used to determine formatting options dependent on the currently active window.

The `[DEFAULT]` section specifies the options that will be used if a matching context definition does not exist, or if a matching context does not specify a custom field value. Contexts can be defined using additional sections in the format `[Executable|Window Title]` where `Executable` and `Window Title` are regex matches for the executable and window title of the active window.

##### Fields:
`font` path to font used. The `MONOSPACED` key can be used to specify a generic monospaced font.

`tabsize` the size of a tab character measured in spaces. Can be float.
