# LaTeX Hotkey Formatter

LHF is a LaTeX to Unicode parser that is activated by a configurable hotkey. When activated, highlighted text will be
reformatted.

## Formatting controls:

Several formatting controls exist, which determine what the formatter will do with any given bit of input.

### LaTeX:

`.t` specifies that a line of text should be interpreted as LaTeX. This flag can only be used at the beginning of a line
and only has an effect when `latex_by_default` is set to 0.

`.r` specifies that a line of text should **not** be interpreted as LaTeX. This flag can only be used at the beginning
of a line and only has an effect when `latex_by_default` is set to 1.

Any text found between two `$` symbols will be treated as LaTeX, regardless of what `latex_by_default` is set to. To
include a regular dollar sign, use `\$`.

### History:

`.h` can be used to retrieve a history entry. By default, it will be replaced with the previous entry. To retrieve
further history `\h[entry_num]` can be used where `entry_num` is the number of entries to look back. `\h[1]` will return
the previous entry, `\h[2]` will return the next previous, and so forth. This flag can be used anywhere within a section
of text.

`.lh[entries]` can be used to retrieve a list of history entries, where `entries` is the number of previous entries to
display. This flag can only be used on its own - no other text must be present.

### Templates:

`.s[name]` and `.l[name]` can be used to save and load templates where `name` is the name of the template to be loaded.

When `\s[name]` is placed at the beginning of the captured string, the rest of the string will be saved as a template.

`.l[name]` can be present anywhere within a string, and it will be replaced with the saved template with that name. If
no template with that name, can be found, it will not be replaced.

Use `.lt` to obtain a list of saved templates and `.d[name]` to delete a template. These flag can only be used on their
own.

## Requirements:

Windows:

```
pynput~=1.7.2
pyperclip~=1.8.1
fonttools~=4.18.2
```

## Config:

### config.ini

```ini
[Formatting Controls]
prefix = .
latex_by_default = 1

[Parser]
show_steps = 0
allow_fraction_shortcut = 1

[Misc]
glyph_width_cache_size = 250
text_width_cache_size = 50
template_save_frequency = 1.0
```

#### Fields:

###### Formatting Controls:

`prefix` prefix to be used for formatting controls such as `.r` and `.t`.

`latex_by_default` if true, input text will be treated as LaTeX unless `.r` as used.

###### Parser:

`show_steps` whether to show each step of LaTeX parsing for debug purposes.

`allow_fraction_shortcut` allows the use of `a/b` and `{a + b}/{c + d}` to denote `\frac{a}{b}` and `\frac{a + b}{c + d}` respectively.

###### Misc:

`glyph_width_cache_size` number of characters to cache within character width lookup function for each font.

`text_width_cache_size` number of strings to cache within text width lookup function for each font.

`template_save_frequency` time in seconds to wait before checking whether templates have changed and need saving.

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

The `[DEFAULT]` section specifies the options that will be used if a matching context definition does not exist, or if a
matching context does not specify a custom field value. Contexts can be defined using additional sections in the
format `[Executable|Window Title]` where `Executable` and `Window Title` are regex matches for the executable and window
title of the active window.

#### Fields:

`font` path to font used. The `MONOSPACED` key can be used to specify a generic monospaced font.

`tabsize` the size of a tab character measured in spaces. Can be float value.

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

**symbols.txt** defines names of symbols within LaTeX. Instances of `\name` will be replaced with the symbol
corresponding to `name`, as defined in the file.

e.g. `\yen` is converted into `¥`.

Comments can be included in the file using the `#` prefix and blank lines are ignored. Pairs of values are separated
with a space.

### symbols/spacing_chars.txt:

```
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?#.°¢£¥®µð𝚤Ƶ𝚥⁇€ℇℎℏℑℓ℘ℜΩ℧℩ÅℲℵℶℷℸ⅁⅄ⅅⅆⅇⅈⅉ♠♡♢♣♤♥♦♧♩♪♫♬♭♮♯✎✓✗µΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψωϐϑϕϖϘϙϚϛϜϝϞϟϠϡϰϱϴϵε϶𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝚨𝚩𝚬𝚭𝚮𝚰𝚱𝚳𝚴𝚶𝚸𝚹𝚻𝚾𝛁𝛐𝛛𝛞𝛢𝛣𝛦𝛧𝛨𝛪𝛫𝛭𝛮𝛰𝛲𝛳𝛵𝛸𝛻𝜊𝜜𝜝𝜠𝜡𝜢𝜤𝜥𝜧𝜨𝜪𝜬𝜭𝜯𝜲𝜵𝝄𝝏𝝒𝝖𝝗𝝚𝝛𝝜𝝞𝝟𝝡𝝢𝝤𝝦𝝧𝝩𝝬𝝯𝝾𝞉𝞌𝞐𝞑𝞔𝞕𝞖𝞘𝞙𝞛𝞜𝞞𝞠𝞡𝞣𝞦𝞩𝞸𝟃𝟆𝟊𝟋Øℕℤℚℝℂℂℊℋℌℍℐℒℕℙℚℛℝℤℨℬℭℯℰℱℳℴℼℽℾℿ⅀𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝒜𝒞𝒟𝒢𝒥𝒦𝒩𝒪𝒫𝒬𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝒶𝒷𝒸𝒹𝒻𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝔄𝔅𝔇𝔈𝔉𝔊𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔𝔖𝔗𝔘𝔙𝔚𝔛𝔜𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔸𝔹𝔻𝔼𝔽𝔾𝕀𝕁𝕂𝕃𝕄𝕆𝕊𝕋𝕌𝕍𝕎𝕏𝕐𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝚪𝚫𝚯𝚲𝚵𝚷𝚺𝚼𝚽𝚿𝛀𝛂𝛃𝛄𝛅𝛆𝛇𝛈𝛉𝛊𝛋𝛌𝛍𝛎𝛏𝛑𝛒𝛓𝛔𝛕𝛖𝛗𝛘𝛙𝛚𝛜𝛝𝛟𝛠𝛡𝜞𝜟𝜣𝜦𝜩𝜫𝜮𝜰𝜱𝜳𝜴𝜶𝜷𝜸𝜹𝜺𝜻𝜼𝜽𝜾𝜿𝝀𝝁𝝂𝝃𝝅𝝆𝝇𝝈𝝉𝝊𝝋𝝌𝝍𝝎𝝐𝝑𝝓𝝔𝝕𝝘𝝙𝝝𝝠𝝣𝝥𝝨𝝪𝝫𝝭𝝮𝝰𝝱𝝲𝝳𝝴𝝵𝝶𝝷𝝸𝝹𝝺𝝻𝝼𝝽𝝿𝞀𝞁𝞂𝞃𝞄𝞅𝞆𝞇𝞈𝞊𝞋𝞍𝞎𝞏𝞒𝞓𝞗𝞚𝞝𝞟𝞢𝞤𝞥𝞧𝞨𝞪𝞫𝞬𝞭𝞮𝞯𝞰𝞱𝞲𝞳𝞴𝞵𝞶𝞷𝞹𝞺𝞻𝞼𝞽𝞾𝞿𝟀𝟁𝟂𝟄𝟅𝟇𝟈𝟉𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿
=<>≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≠≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹⋚⋛⋜⋝⋞⋟⩽⩾⩿⪀⪁⪂⪃⪄⪅⪆⪇⪈⪉⪊⪋⪌⪍⪎⪏⪐⪑⪒⪓⪔⪕⪖⪗⪘⪙⪚⪛⪜⪝⪞⪟⪠
+-±
```

**spacing_chars.txt** defines character spacing rules used to format LaTeX output. All characters found on the first
line of the file have no spacing between characters. All characters found on the second line of the file are equality or
comparison operators, and all characters found on the third line of the file are unary operators.

In practice, characters defined on the first line will clump together into groups and all other characters will be
spaced out. e.g. `6x+7\deg` turns into `6x + 7°`, where `6x` and `7°` have been grouped together.

When an equality or comparison character (second line) is followed by a unary operator (third line), space will not be
included after the unary operator. e.g. `x=-5` turns into `x = -5` instead of `x = - 5`. When an equality or comparison
operator is not present before these unary operators, they will be spaced normally. e.g. `y=x-5` turns into `y = x - 5`.

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

These files define characters which can be mapped into subscript or superscript versions of themselves. When a subscript
or superscript is made entirely of these characters, these characters will be used instead of placing them on the line
above or below.

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

**simple_functions.txt** defines simple functions which have fixed inputs and outputs. Instances of `\func{input}` are
replaced with the corresponding output, as defined in the file, where `func` is the first defined value, `input` is the
second, and the corresponding output is the third defined value.

e.g. `\mathbb{N}` is converted into `ℕ`.

Comments can be included in the file using the `#` prefix and blank lines are ignored. Values are separated with a
space.

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

**variables.txt** defines the conversion between characters, and the corresponding algebraic-style character. These are
not currently used by the formatter.
