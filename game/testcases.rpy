## Happy-path smoke tests for Storeroom Evil.
## Run with:  renpy <project> test <suite::testcase>
## e.g.       renpy . test smoke::start_to_menu


testsuite global:
    before testsuite:
        if not screen "main_menu":
            run MainMenu(confirm=False)

    teardown:
        exit


testsuite smoke:

    setup:
        $ _test.timeout = 90.0
        $ _cb = renpy.test.testexecution.add_reached_label
        $ if _cb not in renpy.config.label_callbacks: renpy.config.label_callbacks.append(_cb)

    testcase start_to_menu:
        description "Start → dialogue → first menu → document reader"
        click "Начать" raw until screen "say"
        advance until screen "choice"
        click "Дебют Гроба" raw until screen "document_reader"
        assert screen "document_reader"


testsuite integrity:
    description "Static integrity checks (labels, items, routing)"

    setup:
        $ _test.timeout = 15.0

    testcase routing_labels_exist:
        description "All chapter labels wired in script.rpy are defined"
        $ expected = [
            "prologue_1", "prologue_2", "prologue_3", "prologue_4",
            "chapter_1_1", "chapter_1_2", "chapter_1_3", "chapter_1_4",
            "chapter_2_1", "chapter_2_2", "chapter_2_3", "chapter_2_4",
            "chapter_3_1", "chapter_3_2", "chapter_3_3", "chapter_3_4",
            "chapter_4_1", "chapter_explore_floor2", "chapter_4_2", "chapter_4_3",
            "demo_end",
        ]
        $ missing = [l for l in expected if not renpy.has_label(l)]
        $ _ok = not missing
        assert eval _ok

    testcase sublabels_exist:
        description "Key event/logic sublabels referenced via call exist"
        $ subs = [
            "ch2_4_mask_assault", "ch2_4_rip_mask", "ch2_4_save_dialog", "ch2_4_death_dialog",
            "parry", "acquire_item",
        ]
        $ missing = [l for l in subs if not renpy.has_label(l)]
        $ _ok = not missing
        assert eval _ok

    testcase items_registry_valid:
        description "Every ITEMS entry has the required name/img keys"
        $ bad = [k for k, v in ITEMS.items() if "name" not in v or "img" not in v]
        $ _ok = not bad
        assert eval _ok

    testcase companions_and_masks_defined:
        description "Companions and core state helpers are defined in store"
        $ _ok = bool(companion_chars) and callable(stat_add) and callable(set_companion) and callable(break_mask) and callable(leon_take_wound)
        assert eval _ok

    testcase location_backgrounds_registered:
        description "Every location bg tag resolves to a cover-scaled image"
        $ _tags = [
            "school_board_office", "street", "gym", "locker_room", "wardrobe",
            "corridor", "assembly_hall", "theater_room", "storage_room",
            "biology", "laboratory", "chemistry_laboratory", "women_toilet",
            "men_toilet", "guard_post", "archive", "generator_room", "medbay",
            "robotics", "math", "teachers_lounge", "cafeteria", "reception",
            "psychologist", "physics", "chemistry", "library", "reading_room",
            "geography", "journalism", "informatics", "rest_room",
            "social_studies", "history", "janitor", "principal_office",
        ]
        $ _imgs = renpy.display.image.images
        $ _missing = [t for t in _tags if ("bg", t) not in _imgs]
        $ _bad = [t for t in _tags if ("bg", t) in _imgs and not isinstance(_imgs[("bg", t)], Transform)]
        $ _ok = (not _missing) and (not _bad)
        assert eval _ok

    testcase enemy_sprites_registered:
        description "All enemy and character sprite images are registered"
        $ _tags = [
            ("leader", "astral"), ("zombie", "guard"), ("skeleton", "warrior"),
            ("ash", "legionnaire"), ("rat", "sprite"), ("newt", "swarm"),
            ("snake", "swarm"),
        ]
        $ _imgs = renpy.display.image.images
        $ _missing = [t for t in _tags if t not in _imgs]
        $ _ok = not _missing
        assert eval _ok

    testcase article_read_cross_chapter_blocked:
        description "Prologue and ch2 article ids share read state"
        $ mark_article_read('sport')
        $ mark_article_read('ch2_chess')
        $ _ok = (is_article_read('sport') and is_article_read('ch2_sport') and is_article_read('chess') and is_article_read('ch2_chess') and not is_article_read('joker') and not is_article_read('ch2_valet') and not is_article_read('notes') and not is_article_read('music'))
        $ read_articles.clear()
        assert eval _ok


testsuite playthrough:
    description "Headless playthrough of every chapter across all companions and all menu/random branches — no two girl sprites on the same slot"
    setup:
        $ _test.timeout = 300.0

    testcase _selftest_overlap_detected:
        $ chapter_test_run("_overlap_self_test", companions=['mari'])
        $ _r = _last_chapter_run
        $ _has_viol = bool(_r['violations'])
        assert eval _has_viol

    testcase prologue_1:
        $ chapter_test_run("prologue_1")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase prologue_2:
        $ chapter_test_run("prologue_2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase prologue_3:
        $ chapter_test_run("prologue_3")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase prologue_4:
        $ chapter_test_run("prologue_4")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_1_1:
        $ chapter_test_run("chapter_1_1")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_1_2:
        $ chapter_test_run("chapter_1_2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_1_3:
        $ chapter_test_run("chapter_1_3")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_1_4:
        $ chapter_test_run("chapter_1_4")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_2_1:
        $ chapter_test_run("chapter_2_1")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_2_2:
        $ chapter_test_run("chapter_2_2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_2_3:
        $ chapter_test_run("chapter_2_3")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_2_4:
        $ chapter_test_run("chapter_2_4")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_3_1:
        $ chapter_test_run("chapter_3_1")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_3_2:
        $ chapter_test_run("chapter_3_2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_3_3:
        $ chapter_test_run("chapter_3_3")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_3_4:
        $ chapter_test_run("chapter_3_4")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_4_1:
        $ chapter_test_run("chapter_4_1")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_4_2:
        $ chapter_test_run("chapter_4_2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_4_3:
        $ chapter_test_run("chapter_4_3")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok

    testcase chapter_explore_floor2:
        $ chapter_test_run("chapter_explore_floor2")
        $ _r = _last_chapter_run
        $ _ok = (not _r['violations'])
        assert eval _ok
