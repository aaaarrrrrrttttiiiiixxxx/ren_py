# Ren'Py Project: ren_py

## File Structure
```
game/
  script.rpy       # Main story script
  options.rpy      # Config (name, version, transitions, window)
  screens.rpy      # All UI screens + styles (1620 lines)
  gui.rpy          # GUI measurements, colors, fonts, sizes
  tl/None/common.rpym  # Russian translations
  gui/             # PNG assets (button/, bar/, slider/, scrollbar/, overlay/)
  gui/phone/       # Mobile variant assets
  images/          # Character sprites by folder: alice/, helena/, sylvia/, mari/, shinna/
  saves/           # Ignored by git
  cache/           # Ignored by git
```
 
## Syntax & Patterns

### define vs default
- `define` — compile-time constant (evaluated once at init)
- `default` — runtime default (can be saved/loaded, persists)
- Examples:
  ```python
  define e = Character('Эйлин', color="#c8ffc8")
  default quick_menu = True
  default preferences.text_cps = 0
  ```

### Characters
```python
define short_name = Character('Display Name', color="#hexcolor")
define narrator = Character(None, color="#ffffff")  # narrator
define side = Character('Name', color="#ffcc00", kind=e)  # inherits from e
```

### Labels (snake_case)
```python
label start:
    scene bg room
    show eileen happy
    e "Dialogue text."
    return

label chapter_1:
    call some_subroutine
    return
```

### Images (auto-defined from `game/images/`)
```python
scene bg room          # from game/images/bg room.png
show eileen happy      # from game/images/eileen happy.webp
show eileen happy at right  # with position
hide eileen
```

### Character sprites (in `game/images/` subdirectories)
All sprites are in folders by character name. Ren'Py auto-defines them as `folder filename-without-ext`. Use spaces in filenames, lowercase.

**Alice Togashi** (Алиса Тогаши) — `game/images/alice/`
```
show alice casual smile
show alice casual smile blush
show alice casual closed smile
show alice casual closed smile blush
show alice casual frown
show alice casual frown blush
show alice casual pout
show alice casual shout
```
Variants: `closed`, `blush` — combine with any expression via spaces.

**Helena Kurosawa** (Хелена Куросава) — `game/images/helena/`
```
show helena casual smile
show helena casual opensmile
show helena casual frown
show helena casual smile blush
show helena casual frown closedeyes
show helena casual opensmile closedeyes blush
```
Expressions: `smile`, `opensmile`, `frown`, with `closedeyes` and/or `blush`.

**Sylvia Kiba** (Сильвия Киба) — `game/images/sylvia/`
```
show sylvia casual smile
show sylvia casual open
show sylvia casual frown blush
show sylvia casual closed smile
show sylvia casual closed open blush
```
Expressions: `smile`, `frown`, `open`, with `closed` and/or `blush`.

**Mari Ayase** (Мари Аясэ) — `game/images/mari/`
```
show mari casual smile
show mari casual opensmile
show mari casual frown
show mari casual smile blush
show mari casual frown eyesclosed
show mari casual opensmile eyesclosed blush
```
Expressions: `smile`, `opensmile`, `frown`, with `eyesclosed`/`closedeyes` and/or `blush`.

**Shinna Kudo** (Шинна Кудо) — `game/images/shinna/`
```
show shinna winter seifuku smile
show shinna winter seifuku frown blush
show shinna winter seifuku closed open
```
Outfit: `winter_seifuku`
Expressions: `smile`, `frown`, `open`, with `closed` and/or `blush`.

### Screens (snake_case)
```python
screen screen_name():
    zorder 100
    style_prefix "prefix"

    vbox:
        textbutton _("Label") action Action()

screen choice(items):
    style_prefix "choice"
    vbox:
        for i in items:
            textbutton i.caption action i.action
```

### Screen special screens
```python
screen say(who, what): ...
screen input(prompt): ...
screen choice(items): ...
screen confirm(message, yes_action, no_action): ...
```

### Styles
```python
style default:
    properties gui.text_properties()
    language gui.language

style button is default:
    properties gui.button_properties("button")

style prefix_button is button:
    xalign 0.5
    size_group "group_name"
```

### Transforms (ATL)
```python
transform delayed_blink(delay, cycle):
    alpha .5
    pause delay
    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat

transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0

transform fade_in_out:
    alpha 0.0
    linear 0.5 alpha 1.0
    pause 1.0
    linear 0.5 alpha 0.0
```

### Transitions
```python
with dissolve
with Dissolve(0.5)
with Fade(0.5, 1.0, 0.5)
with None
scene bg room with dissolve
```

### Python blocks
```python
init python:
    # module-level code
    build.classify('**~', None)

init python:
    config.character_id_prefixes.append('namebox')

init offset = -2  # controls init priority
```

### Menu choices
```python
menu:
    "Option 1":
        call label_1
    "Option 2":
        call label_2
    "Leave":
        return
```

### Character kwargs
```python
define e = Character('Эйлин',
    color="#c8ffc8",
    what_color="#ffffff",
    what_prefix="",
    what_suffix="",
    who_suffix=":",
    ctc="ctc_animation",
    cb_idle="idle_image",
    cb_hover="hover_image",
    cb_selected="selected_image",
)
```

### Audio
```python
play music "track.ogg"
play sound "sfx.ogg"
play voice "voice.ogg"
stop music fadeout 1.0
queue music "next_track.ogg"
```

### Variables / flags
```python
$ variable_name = value
$ persistent.unlock = True  # persistent data

default flag = False  # savable default
```

### NVL mode
```python
define n = Character('Name', kind=nvl)
nvl clear
```

### Bubble (speech bubbles)
```python
define b = Character('Name', kind=bubble)
```
Already configured in gui.rpy / screens.rpy


### Key bindings
```python
key "game_menu" action ShowMenu("preferences")
key "save_delete" action FileDelete(slot)
```

### Common actions
```python
action Return()
action ShowMenu("save")
action ShowMenu("load")
action ShowMenu("preferences")
action Start()
action MainMenu()
action Quit(confirm=True)
action Rollback()
action Skip()
action Preference("text speed", 50)
action FileSave(slot)
action FileLoad(slot)
action FileAction(slot)
action Call("label")
action SetVariable("var", value)
action SetScreenVariable("var", value)
action ToggleVariable("var")
action Play("music", "track.ogg")
```

## Conventions for this project
- Labels: `snake_case` in Russian or English (use consistent choice)
- Characters: lowercase single-letter or short variable names
- Characters: all characters describes in game/characters.rpy
- Screens: `snake_case`, use `style_prefix`, extend existing patterns
- GUI: do NOT change gui.rpy or screens.rpy unless needed for new features
- Images: place in `game/images/` with spaces in names for Ren'Py auto-detection
- Text in `_()` for translatable strings
- Russian locale — keep UI text in Russian
- All custom game logic goes in `script.rpy` or new `.rpy` files in `game/`
