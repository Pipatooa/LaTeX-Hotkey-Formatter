# LaTeX Hotkey Formatter
LHF is a LaTeX to Unicode parser that is activated by a configurable hotkey. When activated, highlighted text will be reformatted.

### Formatting controls:
Several formatting controls exist, which determine what the formatter will do with any given bit of input.

#### LaTeX:
`\t` will convert anything following it from LaTeX into a unicode representation. This flag can only be used at the beginning of a line.

Any text found between two `$` symbols will also be converted from LaTeX into unicode. To include a regular dollar sign, use `\$`.

#### History:
`\h` can be used to retrieve a history entry. By default, it will be replaced with the previous entry. To retrieve further history `\h[entry_num]` can be used where `entry_num` is the number of entries to look back. `\h[1]` will return the previous entry, `\h[2]` will return the next previous, and so forth. This flag can be used anywhere within a section of text.

`\lh[entries]` can be used to retrieve a list of history entries, where `entries` is the number of previous entries to display. This flag can only be used on its own - no other text must be present.

#### Templates:
`\s[name]` and `\l[name]` can be used to save and load templates where `name` is the name of the template to be loaded.

When `\s[name]` is placed at the beginning of the captured string, the rest of the string will be saved as a template.

`\l[name]` can be present anywhere within a string, and it will be replaced with the saved template with that name. If no template with that name, can be found, it will not be replaced.

`\d[name]` can be used to delete a template. This flag can only be used on its own.

To obtain a list of all templates, use `\lt`. This flag can only be used on its own.

### Requirements:
Windows:
```
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
