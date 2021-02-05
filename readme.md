# LaTeX Hotkey Formatter
LHF is a LaTeX to Unicode parser that is activated by a configurable hotkey. When activated, highlighted text will be reformatted.

## Formatting controls:
Several formatting controls exist, which determine what the formatter will do with any given bit of input.

### LaTeX:
`\t` will convert anything following it from LaTeX into a unicode representation. This flag can only be used at the beginning of a line.

Any text found between two `$` symbols will also be converted from LaTeX into unicode. To include a regular dollar sign, use `\$`.

### History:
`\h` can be used to retrieve a history entry. By default, it will be replaced with the previous entry. To retrieve further history `\h[entry_num]` can be used where `entry_num` is the number of entries to look back. `\h[1]` will return the previous entry, `\h[2]` will return the next previous, and so forth. This flag can be used anywhere within a section of text.

`\lh[entries]` can be used to retrieve a list of history entries, where `entries` is the number of previous entries to display. This flag can only be used on its own - no other text must be present.

### Templates:
`\s[name]` and `\l[name]` can be used to save and load templates where `name` is the name of the template to be loaded.

When `\s[name]` is placed at the beginning of the captured string, the rest of the string will be saved as a template.

`\l[name]` can be present anywhere within a string, and it will be replaced with the saved template with that name. If no template with that name, can be found, it will not be replaced.

Use `\lt` to obtain a list of saved templates and `\d[name]` to delete a template. These flag can only be used on their own.

## Requirements:
Windows:
```
pynput~=1.7.2
pyperclip~=1.8.1
fonttools~=4.18.2
```

## Config:
### contexts.ini:
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
The **contexts.ini** file can be used to determine formatting options dependent on the currently active window.

The `[DEFAULT]` section specifies the options that will be used if a matching context definition does not exist, or if a matching context does not specify a custom field value. Contexts can be defined using additional sections in the format `[Executable|Window Title]` where `Executable` and `Window Title` are regex matches for the executable and window title of the active window.

#### Fields:
`font` path to font used. The `MONOSPACED` key can be used to specify a generic monospaced font.

`tabsize` the size of a tab character measured in spaces. Can be float.

### symbols/symbols.txt:
```yaml
# Custom Symbols
deg °

# LaTeX Symbols
lbrack [
backslash \
rbrack ]
sptilde ~
cent ¢
pounds £
yen ¥
```
**symbols.txt** defines the conversion for many of the symbols within LaTeX. Pairs of values are separated with a space. Instances of `\name` will be replaced with the symbol corresponding to `name`, as defined in the file.

Eg. `\yen` is converted into `¥`.

Comments can be included in the file using the `#` prefix and blank lines are ignored.

### symbols/spacing_chars.txt:
```
+-*/=~±·×÷←→→↔∈∉∊∋∌∍∔∝≕∺∻∼∽∾∿≀≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≐≑≒≓≔≖≗≘≙≚≛≜≝≞≟≠≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊏⊐⊑⊒⊕⊖⊗⊘⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿⌀⟵⟶⟷⟸⟹⟺⟻⟼⟽⟾⟿⤀⤁⤂⤃⤄⤅⤆⤇⥊⥋⥎⥐⥒⥓⥖⥗⥚⥛⥞⥟⥢⥤⥦⥧⥨⥩⥪⥫⥬⥭⥶⥷⥸⥹⥺⥻⦓⦔⦕⦖⧤⧥⧺⧻⧼⧽⧾⧿⩦⩧⩨⩩⩪⩫⩬⩭⩮⩯⩰⩱⩲⩳⩴⩵⩶⩷⩸⩹⩺⩻⩼⩽⩾⩿⪀⪁⪂⪃⪄⪅⪆⪇⪈⪉⪊⪋⪌⪍⪎⪏⪐⪑⪒⪓⪔⪕⪖⪗⪘⪙⪚⪛⪜⪝⪞⪟⪠⪡⪢⪣⪤⪥⪦⪧⪨⪩⪪⪫⪬⪭⪮⪯⪰⪱⪲⪳⪴⪵⪶⪷⪸⪹⪺⪻⪼⪽⪾⪿⫀⫁⫂⫃⫄⫅⫆⫇⫈⫉⫊⫋⫌⫏⫐⫑⫒⫓⫔⫕⫖⫗⫘⫷⫸⫹⫺
=≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≠≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹⋚⋛⋜⋝⋞⋟⩽⩾⩿⪀⪁⪂⪃⪄⪅⪆⪇⪈⪉⪊⪋⪌⪍⪎⪏⪐⪑⪒⪓⪔⪕⪖⪗⪘⪙⪚⪛⪜⪝⪞⪟⪠
```
**spacing_chars.txt** defines characters which provide spacing between tokens. All characters found on the first line of the file will automatically provide space between adjacent tokens. All characters found on the second line of the file will overwrite the spacing rules of a following special character. This causes the `-` in `x = -5` to have no spacing between itself and the following `5`.

### symbols/subscript.txt & symbols/superscript.txt:
```
0 ₀
1 ₁
2 ₂
3 ₃
4 ₄
5 ₅
6 ₆
7 ₇
8 ₈
9 ₉
```
These files define characters which can easily be mapped into subscript or superscript versions of themselves. When a subscript or superscript is made entirely of these characters, these characters will be used instead of placing them on the line above or below.

### symbols/simple_functions.txt:
```
mathbb C ℂ
mathcal g ℊ
mathcal H ℋ
mathfrak H ℌ
mathbb H ℍ
mathcal I ℐ
mathcal L ℒ
mathbb N ℕ
mathbb P ℙ
mathbb Q ℚ
```
**simple_functions.txt** defines simple functions which have fixed inputs and outputs. Value triplets are separated with a space. Instances of `\func{input}` are replaced with the corresponding output, as defined in the file, where `func` is the first defined value, `input` is the second, and the corresponding output is the third defined value.

Eg. `\mathbb{N}` is converted into `ℕ`.

Comments can be included in the file using the `#` prefix and blank lines are ignored.

### symbols/variables.txt:
```
a 𝒶
b 𝒷
c 𝒸
d 𝒹
e ℯ
f 𝒻
g ℊ
h 𝒽
i 𝒾
j 𝒿
```
**variables.txt** defines the conversion between characters, and the corresponding algebraic-style character. These are not currently used by the formatter.
