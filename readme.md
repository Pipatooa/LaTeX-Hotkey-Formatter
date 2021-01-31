# Latex Hotkey Formatter
LHF is a latex to Unicode parser that is activated by a configurable hotkey. When pressed, the highlighted text will be reformatted.

### Formatting controls:
Any line of the captured string starting with `\t` will be converted into a unicode equivalent of the 

### Requirements:
some requirements here

### Config:
#### contexts.ini
```ini
[DEFAULT]
font = MONOSPACED

[pycharm64.exe|.*]
font = ./fonts/JetBrainsMono/JetBrainsMono-Light.ttf

[Discord.exe|.*]
font = ./fonts/Whitney/whitneylight.otf

[chrome.exe|Meet - .*]
font = ./fonts/Roboto/Roboto-Regular.ttf
```
###### Usage:
The **contexts.ini** file can be used to determine formatting options dependent on where the currently active window.

The `[DEFAULT]` section specifies the options that will be used if a context definition does not exist, or if a matching context does not specify an option. Contexts can be defined using additional sections in the format `[Executable|Window Title]` where `Executable` and `Window Title` are regex matches for the executable and window title of the active window.

##### Fields:
`font` specifies a path to the font that the active window uses.

`tabsize`