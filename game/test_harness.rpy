## Test harness for headless chapter playthroughs.
##
## Activated only while chapter_test_begin()/chapter_test_end() bracket a run.
##   - menu AND renpy.random.choice: both treated as "decision points" driven
##     by a single schedule list; when no schedule entry exists, a rotating
##     default is used so exploration hubs (while-True menus) terminate.
##   - call_screen: parry_choice -> success; document_reader/item_notification
##     -> no-op.
##   - full_restart (leon_game_over) -> _TestGameOver (death is a valid ending).
##   - fast-skip drives dialogue headlessly.
##   - sprite-overlap: every show/hide/scene is intercepted; a violation is
##     recorded whenever two different girl tags occupy the same slot at once.
##
## chapter_test_run() explores ALL branchable decision points (menus with 2-6
## non-looping options + every random.choice) across ALL five companions, so
## every `elif companion ==` branch and every random-gated branch is exercised.

init python:
    _TEST_GIRL_TAGS = frozenset(['alice', 'mari', 'shinna', 'helena', 'sylvia'])
    _TEST_COMPANIONS = ['mari', 'alice', 'helena', 'shinna', 'sylvia']

    class _TestGameOver(Exception):
        pass

    _test_chapter = {
        'active': False,
        'violations': [],
        'seen': set(),
        'live_slots': {},
        'schedule': [],
        'decision_count': 0,
        'choices_log': [],
        'options_log': [],
        'dec_kinds': [],
        'dec_sigs': [],
        'sig_counts': {},
        'decision_calls': 0,
        'cap': 8000,
        'orig': {},
    }

    _TEST_SLOT_THRESHOLD = 0.15

    _TEST_XPOS = {
        'far_left': 0.12, 'left_edge': 0.0, 'left': 0.30,
        'center': 0.50, 'right': 0.70, 'right_edge': 1.0, 'far_right': 0.88,
    }

    def _test_pos_of(at):
        for t in (at or []):
            if t is sprite_far_left or t is far_left:
                return ('far_left', 0.12)
            if t is sprite_far_right or t is far_right:
                return ('far_right', 0.88)
            if t is sprite_left:
                return ('left', 0.30)
            if t is left:
                return ('left', 0.0)
            if t is sprite_right:
                return ('right', 0.70)
            if t is right:
                return ('right', 1.0)
            if t is center or t is sprite_center:
                return ('center', 0.5)
            xp = getattr(t, 'xpos', None)
            xa = getattr(t, 'xalign', None)
            if xp is not None:
                return (None, float(xp))
            if xa is not None:
                return (None, float(xa))
        return None

    def _test_slot_of(at):
        pos = _test_pos_of(at)
        if pos is None:
            return None
        slot, xp = pos
        if slot is not None:
            return slot
        if abs(xp - 0.12) < 0.001:
            return 'far_left'
        if abs(xp - 0.88) < 0.001:
            return 'far_right'
        if abs(xp - 0.30) < 0.001:
            return 'left'
        if abs(xp - 0.70) < 0.001:
            return 'right'
        if abs(xp - 0.5) < 0.001:
            return 'center'
        return 'x:%.2f' % xp

    def _test_tag_of(name, tag):
        if tag:
            return tag
        if isinstance(name, (tuple, list)):
            return name[0] if name else None
        if name is None:
            return None
        return str(name).split(' ', 1)[0]

    def _test_record_girl_show(t, at_list):
        live = _test_chapter['live_slots']
        pos = _test_pos_of(at_list)
        if pos is not None:
            slot, xp = pos
            if slot is None:
                slot = 'x:%.2f' % xp
        elif t in live:
            slot, xp = live[t]
        else:
            slot, xp = 'center', 0.5
        for other, (oslot, oxp) in live.items():
            if other == t:
                continue
            same_slot = (oslot == slot)
            close_x = (abs(oxp - xp) < _TEST_SLOT_THRESHOLD)
            if same_slot or close_x:
                key = (round(xp, 3), tuple(sorted([t, other])))
                if key not in _test_chapter['seen']:
                    _test_chapter['seen'].add(key)
                    kind = 'slot' if same_slot else 'xpos'
                    _test_chapter['violations'].append(
                        "%s %.2f+%.2f: %s + %s" % (kind, xp, oxp, t, other))
        live[t] = (slot, xp)


    def _test_show_wrap(name, at_list=None, layer=None, what=None, tag=None, **kwargs):
        if at_list is None:
            at_list = []
        if _test_chapter['active'] and (layer in (None, 'master')):
            t = _test_tag_of(name, tag)
            if t in _TEST_GIRL_TAGS:
                _test_record_girl_show(t, at_list)
        return _test_chapter['orig']['show'](name, at_list=at_list, layer=layer, what=what, tag=tag, **kwargs)

    def _test_hide_wrap(name, layer=None, *args, **kwargs):
        if _test_chapter['active'] and (layer in (None, 'master')):
            t = _test_tag_of(name, None)
            _test_chapter['live_slots'].pop(t, None)
        return _test_chapter['orig']['hide'](name, layer=layer, *args, **kwargs)

    def _test_scene_wrap(layer='master', *args, **kwargs):
        if _test_chapter['active'] and (layer in (None, 'master')):
            _test_chapter['live_slots'].clear()
        return _test_chapter['orig']['scene'](layer, *args, **kwargs)

    def _test_decide(n, kind, sig):
        tc = _test_chapter
        tc['decision_calls'] += 1
        if tc['decision_calls'] > tc['cap']:
            raise Exception("chapter_test: decision cap exceeded (infinite loop?)")
        i = tc['decision_count']
        tc['decision_count'] += 1
        tc['options_log'].append(n)
        tc['dec_kinds'].append(kind)
        tc['dec_sigs'].append(sig)
        cnt = tc['sig_counts'].get(sig, 0)
        tc['sig_counts'][sig] = cnt + 1
        sched = tc['schedule']
        if i < len(sched):
            idx = min(max(int(sched[i]), 0), n - 1)
        elif cnt >= n * 3:
            idx = n - 1
        else:
            idx = cnt % n
        tc['choices_log'].append(idx)
        return idx

    def _test_menu_override(items, set_expr, args=None, kwargs=None, item_arguments=None):
        choosable = [(l, c, v) for (l, c, v) in items if renpy.python.py_eval(c)]
        if not choosable:
            return None
        n = len(choosable)
        try:
            sig = ('menu', n, tuple(l for (l, c, v) in choosable))
        except Exception:
            sig = ('menu', n)
        idx = _test_decide(n, 'menu', sig)
        return choosable[idx][2]

    def _test_random_choice_override(seq):
        try:
            seq = list(seq)
        except Exception:
            seq = [seq]
        n = len(seq)
        if n == 0:
            raise IndexError("nothing to choose")
        sig = ('rchoice', n)
        idx = _test_decide(n, 'rchoice', sig)
        return seq[idx]

    def _test_call_screen_override(_screen_name, *args, **kwargs):
        if _screen_name == 'parry_choice':
            items = kwargs.get('items')
            if not items and args:
                items = args[0]
            if items:
                return items[0][1]
            return '__miss__'
        if _screen_name in ('document_reader', 'item_notification'):
            return None
        return _test_chapter['orig']['call_screen'](_screen_name, *args, **kwargs)

    def _test_full_restart_override(*args, **kwargs):
        raise _TestGameOver("leon_game_over")

    def chapter_test_begin(schedule=None):
        import time
        try:
            renpy.execution.il_first_deadline = time.time() + 100000.0
            renpy.execution.il_second_deadline = 0.0
            renpy.execution.il_statements = 0
        except Exception:
            pass
        o = _test_chapter['orig']
        o['show'] = renpy.exports.show
        o['hide'] = renpy.exports.hide
        o['scene'] = renpy.exports.scene
        o['menu'] = renpy.exports.menu
        o['call_screen'] = renpy.call_screen
        o['full_restart'] = renpy.full_restart
        o['rchoice'] = renpy.random.choice
        o['skipping'] = renpy.config.skipping
        o['allow_skipping'] = renpy.config.allow_skipping
        o['_skipping'] = _skipping
        renpy.exports.show = _test_show_wrap
        renpy.config.show = _test_show_wrap
        renpy.exports.hide = _test_hide_wrap
        renpy.config.hide = _test_hide_wrap
        renpy.exports.scene = _test_scene_wrap
        renpy.config.scene = _test_scene_wrap
        renpy.exports.menu = _test_menu_override
        renpy.call_screen = _test_call_screen_override
        renpy.full_restart = _test_full_restart_override
        renpy.random.choice = _test_random_choice_override
        renpy.config.allow_skipping = True
        renpy.store._skipping = True
        renpy.config.skipping = 'fast'
        _test_chapter['active'] = True
        _test_chapter['violations'] = []
        _test_chapter['seen'] = set()
        _test_chapter['live_slots'] = {}
        _test_chapter['schedule'] = list(schedule) if schedule else []
        _test_chapter['decision_count'] = 0
        _test_chapter['choices_log'] = []
        _test_chapter['options_log'] = []
        _test_chapter['dec_kinds'] = []
        _test_chapter['dec_sigs'] = []
        _test_chapter['sig_counts'] = {}
        _test_chapter['decision_calls'] = 0

    def chapter_test_end():
        o = _test_chapter['orig']
        renpy.exports.show = o['show']
        renpy.config.show = o['show']
        renpy.exports.hide = o['hide']
        renpy.config.hide = o['hide']
        renpy.exports.scene = o['scene']
        renpy.config.scene = o['scene']
        renpy.exports.menu = o['menu']
        renpy.call_screen = o['call_screen']
        renpy.full_restart = o['full_restart']
        renpy.random.choice = o['rchoice']
        renpy.config.skipping = o['skipping']
        renpy.config.allow_skipping = o['allow_skipping']
        renpy.store._skipping = o['_skipping']
        _test_chapter['active'] = False

    def _chapter_test_reset_state(companion_girl='mari'):
        renpy.random.seed(1234)
        for g in ['alice', 'mari', 'shinna', 'helena', 'sylvia']:
            base = {
                'alice': {'strength': 0, 'intellect': 3, 'organization': 2, 'mysticism': 1, 'empathy': 1},
                'mari': {'strength': 1, 'intellect': 2, 'organization': 1, 'mysticism': 2, 'empathy': 3},
                'shinna': {'strength': 2, 'intellect': 3, 'organization': 3, 'mysticism': 1, 'empathy': 2},
                'helena': {'strength': 1, 'intellect': 3, 'organization': 2, 'mysticism': 3, 'empathy': 2},
                'sylvia': {'strength': 3, 'intellect': 1, 'organization': 1, 'mysticism': 1, 'empathy': 2},
            }[g]
            char_stats[g] = dict(base)
        char_stats['leon'] = {'strength': 5, 'intellect': 3, 'organization': 3, 'mysticism': 2, 'empathy': 2}
        global leon_wounds, inventory, saved_girls, dead_girls, met_girls, read_articles
        global possessed_girl, possessed_mask, companion, companion_display, first_girl
        global girl_alive, mask_broken
        leon_wounds = 0
        read_articles = []
        inventory = {}
        saved_girls = []
        dead_girls = []
        met_girls = []
        possessed_girl = None
        possessed_mask = None
        companion = None
        companion_display = None
        first_girl = None
        girl_alive = True
        mask_broken = False
        for k in mask_intact:
            mask_intact[k] = True
        party[:] = ['leon']
        set_companion(companion_girl)
        for it in ['occult_diary', 'kerosene_lamp', 'fire_extinguisher', 'water_bucket', 'alcohol_bottle', 'bat', 'map_floor_1']:
            give_item(it)

    def _run_once(label, companion_girl, schedule):
        _chapter_test_reset_state(companion_girl)
        chapter_test_begin(schedule)
        error = None
        ended_by = 'return'
        try:
            renpy.call_in_new_context(label)
        except _TestGameOver:
            ended_by = 'game_over'
        except Exception as e:
            import traceback
            error = traceback.format_exc()
        finally:
            chapter_test_end()
        return {
            'companion': companion_girl,
            'schedule': list(schedule),
            'ended_by': ended_by,
            'error': error,
            'violations': list(_test_chapter['violations']),
            'choices_log': list(_test_chapter['choices_log']),
            'options_log': list(_test_chapter['options_log']),
            'dec_kinds': list(_test_chapter['dec_kinds']),
            'dec_sigs': list(_test_chapter['dec_sigs']),
        }

    def _branchable(i, r):
        opts = r['options_log']
        sigs = r['dec_sigs']
        if i >= len(opts):
            return False
        n = opts[i]
        if n <= 1:
            return False
        if n > 6:
            return False
        if sigs[:i].count(sigs[i]) >= 1:
            return False
        return True

    def chapter_test_run(label, companions=None, max_runs=100, branch=True):
        if companions is None:
            companions = _TEST_COMPANIONS
        agg_viol = []
        agg_err = []
        total = 0
        for comp in companions:
            explored = set()
            stack = [()]
            while stack and total < max_runs:
                sched = stack.pop()
                if sched in explored:
                    continue
                explored.add(sched)
                r = _run_once(label, comp, list(sched))
                total += 1
                for v in r['violations']:
                    s = "[comp=%s] %s" % (comp, v)
                    if s not in agg_viol:
                        agg_viol.append(s)
                if r['error']:
                    lines = r['error'].strip().splitlines()
                    short = lines[-1] if lines else 'error'
                    agg_err.append("[comp=%s sched=%s] %s" % (comp, list(sched), short))
                if not branch:
                    continue
                ch = r['choices_log']
                for i in range(len(ch)):
                    if not _branchable(i, r):
                        continue
                    chosen = ch[i]
                    n = r['options_log'][i]
                    for o in range(n):
                        if o == chosen:
                            continue
                        child = tuple(ch[:i]) + (o,)
                        if child not in explored:
                            stack.append(child)
        result = {
            'label': label,
            'violations': agg_viol,
            'errors': agg_err,
            'runs': total,
        }
        renpy.store._last_chapter_run = result
        try:
            import os
            with open(os.path.join('/tmp', 'opencode', 'chapter_runs.txt'), 'a') as _f:
                _f.write("%s\truns=%d\tviol=%d\terr=%d\t%s\n" % (
                    label, total, len(agg_viol), len(agg_err),
                    '; '.join(agg_viol) or '-'))
                for e in agg_err:
                    _f.write("  ERR %s\n" % e)
        except Exception:
            pass
        return result
