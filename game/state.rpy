define STRENGTH = 'strength'
define INTELLECT = 'intellect'
define ORGANIZATION = 'organization'
define MYSTICISM = 'mysticism'
define EMPATHY = 'empathy'

define STAT_ORDER = ['strength', 'intellect', 'organization', 'mysticism', 'empathy']

define STAT_LABELS = {
    'strength': 'Сила',
    'intellect': 'Интеллект',
    'organization': 'Организованность',
    'mysticism': 'Мистицизм',
    'empathy': 'Эмпатия',
}

define STAT_ICONS = {
    'strength': 'ui_strength',
    'intellect': 'ui_intellect',
    'organization': 'ui_organization',
    'mysticism': 'ui_mysticism',
    'empathy': 'ui_empathy',
}

default char_stats = {
    'leon':     {'strength': 1, 'intellect': 1, 'organization': 1, 'mysticism': 1, 'empathy': 1},
    'alice':    {'strength': 0, 'intellect': 3, 'organization': 2, 'mysticism': 1, 'empathy': 1},
    'mari':     {'strength': 1, 'intellect': 2, 'organization': 1, 'mysticism': 2, 'empathy': 3},
    'shinna':   {'strength': 2, 'intellect': 3, 'organization': 3, 'mysticism': 1, 'empathy': 2},
    'helena':   {'strength': 1, 'intellect': 3, 'organization': 2, 'mysticism': 3, 'empathy': 2},
    'sylvia':   {'strength': 3, 'intellect': 1, 'organization': 1, 'mysticism': 1, 'empathy': 2},
}

default party = ['leon']
default companion = None
default companion_display = None
default first_girl = None
default saved_girls = []
default dead_girls = []
default met_girls = []
default possessed_girl = None
default possessed_mask = None
default mask_intact = {'genro': True, 'dokuto': True, 'burai': True, 'kara': True}

default leon_wounds = 0

default inventory = {}
default read_articles = []
default read_documents = []
default visited_rooms = []
default done_actions = []

default current_chapter = None
default current_scene = None
default current_location = None

default _group_table_expanded = False

init python:
    def stat_get(name, stat):
        return char_stats[name][stat]

    GIRL_NAMES = {
        'leon': 'Леон', 'alice': 'Алиса', 'mari': 'Мари',
        'shinna': 'Шинна', 'helena': 'Хелена', 'sylvia': 'Сильвия',
    }

    def girl_name(girl_id):
        return GIRL_NAMES.get(girl_id, 'девушка')

    def companion_name():
        return girl_name(companion) if companion else 'девушка'

    def stat_add(name, stat, delta=1):
        char_stats[name][stat] += delta

    def in_party(name):
        return name in party

    def party_join(name):
        if name not in party:
            party.append(name)

    def party_leave(name):
        if name in party:
            party.remove(name)

    def group_stat(stat):
        if not party:
            return 0
        return max(char_stats[p][stat] for p in party)

    def group_max_contributors(stat):
        if not party:
            return []
        mx = group_stat(stat)
        return [p for p in party if char_stats[p][stat] == mx]

    def group_meets(stat, threshold):
        return group_stat(stat) >= threshold

    def set_companion(girl_id):
        global companion, companion_display
        for g in ['alice', 'mari', 'shinna', 'helena', 'sylvia']:
            if g != girl_id and g in party:
                party.remove(g)
        companion = girl_id
        companion_display = girl_name(girl_id) if girl_id else None
        if girl_id is not None:
            party_join(girl_id)

    def set_possessed(girl_id, mask_id):
        global possessed_girl, possessed_mask
        possessed_girl = girl_id
        possessed_mask = mask_id
        if girl_id in party:
            party.remove(girl_id)

    def clear_possessed():
        global possessed_girl, possessed_mask
        possessed_girl = None
        possessed_mask = None

    def mark_saved(girl_id):
        if girl_id in dead_girls:
            dead_girls.remove(girl_id)
        if girl_id not in saved_girls:
            saved_girls.append(girl_id)
        clear_possessed()

    def mark_dead(girl_id):
        if girl_id in saved_girls:
            saved_girls.remove(girl_id)
        if girl_id not in dead_girls:
            dead_girls.append(girl_id)
        if girl_id in party:
            party.remove(girl_id)
        if possessed_girl == girl_id:
            clear_possessed()

    def break_mask(mask_id):
        mask_intact[mask_id] = False

    def give_item(item_id, count=1):
        inventory[item_id] = inventory.get(item_id, 0) + count

    def remove_item(item_id, count=1):
        if item_id not in inventory:
            return False
        if inventory[item_id] < count:
            return False
        inventory[item_id] -= count
        if inventory[item_id] <= 0:
            del inventory[item_id]
        return True

    def has_item(item_id, count=1):
        return inventory.get(item_id, 0) >= count

    def mark_visited(room_id):
        if room_id not in visited_rooms:
            visited_rooms.append(room_id)

    def is_visited(room_id):
        return room_id in visited_rooms

    def mark_action_done(action_id):
        if action_id not in done_actions:
            done_actions.append(action_id)

    def action_done(action_id):
        return action_id in done_actions

    ARTICLE_ALIASES = {
        'ch2_sport': 'sport',
        'ch2_chess': 'chess',
        'ch2_valet': 'joker',
        'ch2_notes': 'notes',
        'ch2_music': 'music',
    }

    def _article_canonical(article_id):
        return ARTICLE_ALIASES.get(article_id, article_id)

    def mark_article_read(article_id):
        article_id = _article_canonical(article_id)
        if article_id not in read_articles:
            read_articles.append(article_id)

    def is_article_read(article_id):
        return article_id in read_articles or _article_canonical(article_id) in read_articles

    def mark_document_read(doc_id):
        if doc_id not in read_documents:
            read_documents.append(doc_id)

    def _decrease_leon_max_stat():
        st = char_stats['leon']
        mx = max(st.values())
        if mx <= 0:
            renpy.call_in_new_context('leon_game_over')
            return
        for k in STAT_ORDER:
            if st[k] == mx:
                st[k] -= 1
                return

    def leon_take_wound():
        global leon_wounds
        limit = char_stats['leon']['strength']
        if limit <= 0:
            _decrease_leon_max_stat()
            return
        leon_wounds += 1
        if leon_wounds >= limit:
            leon_wounds = 0
            _decrease_leon_max_stat()

    def leon_wound_limit():
        return char_stats['leon']['strength']

    def leon_heal_wound():
        global leon_wounds
        if leon_wounds > 0:
            leon_wounds -= 1
