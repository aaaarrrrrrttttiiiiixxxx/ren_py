# Вы можете расположить сценарий своей игры в этом файле.

# Определение персонажей игры.
define e = Character('Эйлин', color="#c8ffc8")


# Вместо использования оператора image можете просто
# складывать все ваши файлы изображений в папку images.
# Например, сцену bg room можно вызвать файлом "bg room.png",
# а eileen happy — "eileen happy.webp", и тогда они появятся в игре.

# Игра начинается здесь:
label start:
    show screen group_panel
    # call demo_panorama

    # call prologue_1
    # call prologue_2
    # call prologue_3
    # call prologue_4

    # call chapter_1_1
    # call chapter_1_2
    # call chapter_1_3
    call chapter_1_4

    call chapter_2_1
    call chapter_2_2
    call chapter_2_3
    call chapter_2_4

    call chapter_3_1
    call chapter_3_2
    call chapter_3_3
    call chapter_3_4

    call chapter_4_1
    call chapter_explore_floor2
    call chapter_4_2
    call chapter_4_3

    call demo_end

    return


label leon_game_over:
    scene black with dissolve
    centered "Силы Леона иссякли..."
    centered "Игра окончена."
    $ renpy.full_restart()


label demo_end:
    scene black with dissolve
    centered "Конец доступной части."
    centered "Продолжение следует..."
    return
