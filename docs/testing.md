# Testing

Tests live in `game/testcases.rpy` and use Ren'Py's built-in test framework
(`testsuite` / `testcase` statements). Add new tests there. The headless chapter
runner lives in `game/test_harness.rpy`; its self-test fixture is in
`game/test_fixtures.rpy`.

## Running

From the repo root, run the full suite:

```
renpy . test
```

Run one testcase by id (ids use `::`, e.g. `smoke::start_to_menu`,
`playthrough::chapter_3_1`):

```
renpy . test playthrough::chapter_3_1
```

Useful flags: `--hide-header`, `--report-detailed`.

## Requirements

- Tests need a **real display** (`DISPLAY=:0`). `SDL_VIDEODRIVER=dummy` hangs.
- Exit code 0 = pass, 1 = fail. CI should fail the build on non-zero.

## Test DSL cheat-sheet

```
testsuite name:          # a group of tests
    setup:               # runs once (set $ _test.timeout = N)
        ...
    before testcase:     # runs before each testcase
        ...
    testcase my_test:    # an individual test
        description "..."
        click "Начать" raw until screen "say"   # click button by text, wait for screen
        advance until screen "choice"           # advance dialogue until a screen appears
        assert screen "document_reader"         # assert a screen is shown
        $ _ok = renpy.has_label("demo_end")     # run python in store scope
        assert eval _ok                         # assert a python expression (BARE name)
        pause 0.5                               # fixed delay

testsuite global:        # special: wraps every other suite
    before testsuite:
        if not screen "main_menu":
            run MainMenu(confirm=False)
    teardown:
        exit                                 # quit the game after the run
```

### Key statements

| Statement | Purpose |
|---|---|
| `click "text" raw until <cond>` | click a button by text, repeat until condition |
| `advance until <cond>` | advance dialogue until condition (screen / label / text) |
| `assert screen "name"` | assert a screen is currently shown |
| `assert eval <expr>` | assert a python expression is truthy (**see gotcha below**) |
| `$ code` | run python in store scope |
| `pause N` | fixed delay in seconds |
| `run Action()` | run a screen action (e.g. `Start()`, `MainMenu(confirm=False)`) |

Conditions can use: `screen "name"`, `not screen "name"`, `label "name"`,
`eval <expr>`, `"text" raw`, combined with `and` / `or` / `not`.

## CRITICAL gotcha: `assert eval` needs a BARE expression

`assert eval` captures its argument with Ren'Py's `simple_expression` lexer and
calls `bool()` on the result. **If you quote it, you are asserting a non-empty
string literal, which is always true** — the check becomes a no-op:

```renpy
# WRONG — always passes (asserts the truthy string "not missing"):
assert eval "not missing"

# RIGHT — assert a bare name (bool of the actual value):
$ _ok = not missing
assert eval _ok
```

`simple_expression` matches a name with optional `.attr`, `[index]`, `(call)` —
it does **not** include `not`/`and`/`or`. So for compound logic, precompute into
a single boolean name first, then `assert eval _ok`. This is why every
`assert eval` in this project is preceded by a `$ _ok = ...` line.

## Suites

### `smoke`
- **`start_to_menu`** — Start → dialogue → first menu → document reader. Covers
  the core advance → menu → screen flow.

### `integrity`
Static checks (no display driving). Add a check here when you wire a new chapter
label or item — these catch "label not found" crashes deterministically.
- **`routing_labels_exist`** — all chapter labels wired in `script.rpy` exist.
- **`sublabels_exist`** — key event/logic sublabels referenced via `call` exist.
- **`items_registry_valid`** — every `ITEMS` entry has the required `name`/`img` keys.
- **`companions_and_masks_defined`** — `companion_chars` and core state helpers
  (`stat_add`, `set_companion`, `break_mask`, `leon_take_wound`) are defined.

### `playthrough`
Headless full playthrough of **every story label** — one testcase per
`prologue_*` and `chapter_*_*` label. Each runs the whole label (and every label
it `call`s) without UI interaction and asserts two invariants:

1. **No crash** — the label reaches `return` (or a valid game-over) without
   raising a Python exception.
2. **No two girl sprites on the same slot** — at no point may two different
   character tags (`alice`, `mari`, `shinna`, `helena`, `sylvia`) be shown at the
   same on-screen position at once.

There is also **`_selftest_overlap_detected`**, a self-test that intentionally
shows two girls on the same slot and asserts the harness reports a violation —
it guarantees the overlap detector itself works.

#### Sprite positions and the overlap rule
The detector classifies every shown girl into one of five horizontal slots and
flags two different girl tags sharing a slot:

| slot | xpos | transforms |
|---|---|---|
| `far_left` | 0.12 | `sprite_far_left` / `far_left` |
| `left` | 0.0–0.30 | built-in `left`, `sprite_left` |
| `center` | 0.5 | built-in `center` / `sprite_center`, and **no-`at` default** |
| `right` | 0.70–1.0 | built-in `right`, `sprite_right` |
| `far_right` | 0.88 | `sprite_far_right` / `far_right` |

Notes for staging scenes:
- **`show X` with no `at` lands at center** (Ren'Py default placement) — it
  collides with a girl shown `at center`. The detector treats them as the same
  slot.
- **Sticky positions**: re-showing the *same* tag without `at` keeps its last
  slot (the detector models this). So `show alice smile at left` then
  `show alice frown` leaves alice at `left`.
- **Group scenes (4–5 girls)**: there are only five slots. Use `far_left`/
  `far_right` (defined in `game/sprite_registry.rpy`) for the outer girls; never
  stack two girls on the same slot. If a scene needs to swap girls, `hide` the
  outgoing one first.
- Keep one transform family per scene (`sprite_*` or built-in, not mixed) —
  built-in `left` (edge-anchored, 0.0) and `sprite_left` (center-anchored, 0.30)
  are different visual positions and mixing them reads as inconsistent staging.

## The chapter-test harness (`game/test_harness.rpy`)

`chapter_test_run("chapter_X_Y")` runs a chapter headlessly. It is only active
between `chapter_test_begin()` / `chapter_test_end()`, so it does not affect the
other suites. While active it:

- **Resets state** to a clean mid-game fixture (companion=`mari`, all common
  items granted, stats reset, masks intact, RNG seeded for determinism).
- **Auto-picks menus** by overriding `renpy.exports.menu`: it filters to the
  choosable items and returns them **rotating** (a global counter cycles through
  the list). Rotation is what lets exploration hubs with an unconditional exit
  (e.g. `chapter_explore_floor2`) terminate — the exit choice is eventually hit.
  A menu cap (default 2000) guards against real infinite loops.
- **Bypasses blocking screens** by overriding `renpy.call_screen`:
  `parry_choice` → success (first item's value), `document_reader` /
  `item_notification` → no-op.
- **Treats death as a valid ending**: `renpy.full_restart` (leon_game_over) is
  overridden to raise `_TestGameOver`, which the runner catches — the chapter is
  recorded as `ended_by='game_over'`, not a crash.
- **Fast-skips dialogue** (`config.skipping='fast'`) so says do not block.
- **Detects sprite overlap** by wrapping `renpy.exports.show` / `renpy.config.show`
  (and `hide` / `scene`): every girl `show` is recorded into a live `{tag: slot}`
  map, and showing a girl into a slot already held by a *different* girl tag
  records a violation. (`renpy.config.show` is `renpy.exports.show`, but it holds
  the original reference, so both the statement path and the python path
  `c_show`/`show_girl` must be patched.)

Results are left in `store._last_chapter_run` (`label`, `ended_by`, `error`,
`violations`, `menu_calls`) and, for diagnostics, appended to
`/tmp/opencode/chapter_runs.txt`.

### Adding a story-label test

When you add a new `prologue_*` or `chapter_X_Y` label, add a testcase to the
`playthrough` suite:

```
testcase chapter_X_Y:
    $ chapter_test_run("chapter_X_Y")
    $ _r = _last_chapter_run
    $ _ok = (not _r['error']) and (not _r['violations'])
    assert eval _ok
```

If the label needs different starting state (a specific companion, an item
absent, a mask broken), extend `_chapter_test_reset_state()` or set it inside the
testcase before calling `chapter_test_run`.

## Other gotchas

- **Fast-skip stalls at menus.** `skip fast until label X` does NOT auto-pick
  choices. The playthrough harness solves this by overriding
  `renpy.exports.menu`; if you drive menus by hand in a `smoke` test, use
  `advance until screen "choice"` then `click "choice text" raw`.
- **`until label X` needs the label callback.** Register
  `renpy.test.testexecution.add_reached_label` in your suite `setup` if you use it.
- **Test isolation**: `MainMenu(confirm=False)` does not reliably reset from deep
  in a call stack. Keep each `smoke` testcase a single continuous flow.
- **Path coverage**: the playthrough harness auto-picks one path per menu (with
  rotation across repeated menus). It does NOT exhaustively walk every branch.
  Branches not on the auto-picked path are not exercised — review complex
  `menu`/`while` blocks manually when you change them.
