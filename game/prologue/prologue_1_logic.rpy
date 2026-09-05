# Пролог 1: Логика выбора
# Основан на файле "Диалоги/Пролог 1 Кабинет Школьного совета.md"

label prologue_1:
    call pro_1_meeting
    call pro_1_go_for_food
    call pro_1_assign_tasks
    call pro_1_article_choice
    call pro_1_finish_work

    return


label pro_1_article_choice:
    menu:
        "Выберите статью для проверки:"

        "«Спорт калечит — физкультура лечит» — важность безопасного спорта и анализ здоровья своего организма." if not is_article_read('sport'):
            call pro_1_article_sport

        "«Дебют Гроба» — сильнейшее начало на шахматном турнире." if not is_article_read('chess'):
            call pro_1_article_chess

        "«Легенда о бубновом валете» — призрак, вызываемый через экран монитора?" if not is_article_read('joker'):
            call pro_1_article_joker

        "«Второй мозг» — Как организовать хранение большого объема информации?" if not is_article_read('notes'):
            call pro_1_article_notes

        "«На одной волне» — Как музыка помогает человеку разобраться в себе?" if not is_article_read('music'):
            call pro_1_article_music

    return
