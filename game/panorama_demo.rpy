define pan_range = 240

define pan360_zoom = 1080.0 / 346
define pan360_w = int(1024 * pan360_zoom)


image bg wide_panorama:
    "images/1.jpg"
    zoom 4


image bg wide_panorama_360 = Composite(
    (pan360_w * 2, 1080),
    (0, 0), Transform("images/1.jpg", zoom=pan360_zoom),
    (pan360_w, 0), Transform("images/1.jpg", zoom=pan360_zoom),
)


transform pan_hold(x=0):
    crop (x, 0, 1920, 1080)


transform pan_scan(x_from, x_to, duration=5.0):
    crop (x_from, 0, 1920, 1080)
    linear duration crop (x_to, 0, 1920, 1080)


screen panorama_explore():
    viewport:
        xsize 1920
        ysize 1080
        draggable True
        edgescroll (200, 600)
        add "bg wide_panorama"

    textbutton _("Продолжить"):
        xalign 0.5
        yalign 0.95
        action Return()


init python:
    import pygame

    def keyboard_pan_tick(adj, speed=20):
        pressed = pygame.key.get_pressed()
        dx = 0
        if pressed[pygame.K_a]:
            dx -= speed
        if pressed[pygame.K_d]:
            dx += speed
        if dx == 0:
            return
        rng = adj.range
        if not rng:
            return
        new_v = adj.value + dx
        if new_v < 0:
            new_v = 0
        elif new_v > rng:
            new_v = rng
        adj.change(new_v)

    def keyboard_pan360_tick(adj, speed=10):
        pressed = pygame.key.get_pressed()
        dx = 0
        if pressed[pygame.K_a]:
            dx -= speed
        if pressed[pygame.K_d]:
            dx += speed
        if dx == 0:
            return
        adj.change((adj.value + dx) % pan360_w)


screen keyboard_panorama():
    default adj = ui.adjustment(range=pan_range, value=0, adjustable=True)

    viewport:
        xsize 1920
        ysize 1080
        xadjustment adj
        draggable True
        edgescroll (200, 600)
        add "bg wide_panorama"

    timer 0.02 repeat True action Function(keyboard_pan_tick, adj, 5)

    text _("Зажмите Ф (A) — влево, В (D) — вправо"):
        xalign 0.5
        yalign 0.05
        color "#ffffff"
        outlines [(2, "#000000", 0, 0)]

    textbutton _("Продолжить"):
        xalign 0.5
        yalign 0.95
        action Return()


screen keyboard_panorama_360():
    default adj = ui.adjustment(range=pan360_w, value=0, adjustable=True)

    viewport:
        xsize 1920
        ysize 1080
        xadjustment adj
        child_size (pan360_w + 1920, 1080)
        draggable True
        add "bg wide_panorama_360"

    timer 0.02 repeat True action Function(keyboard_pan360_tick, adj, 10)

    text _("Зажмите Ф (A) — влево, В (D) — вправо. Край не кончится — это 360°"):
        xalign 0.5
        yalign 0.05
        color "#ffffff"
        outlines [(2, "#000000", 0, 0)]

    textbutton _("Продолжить"):
        xalign 0.5
        yalign 0.95
        action Return()


label demo_panorama:
    scene bg wide_panorama at pan_hold(0)
    with dissolve


    n "А теперь — интерактивный режим: перетаскивайте фон мышью или подведите курсор к краям."
    call screen panorama_explore

    n "А теперь — бесконечная прокрутка на 360°. Зажмите Ф (A) — влево, В (D) — вправо."
    n "Горизонтальных краёв нет: крутите сколько угодно, фон продолжается той же картинкой. Верх и низ остаются на месте."
    call screen keyboard_panorama_360
    scene black with dissolve

    return
