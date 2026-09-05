image helena frown blush:
    "images/helena/helena_frown_blush.png"
    zoom 0.815
image helena frown closedeyes blush:
    "images/helena/helena_frown_closedeyes_blush.png"
    zoom 0.815
image helena frown closedeyes:
    "images/helena/helena_frown_closedeyes.png"
    zoom 0.815
image helena frown:
    "images/helena/helena_frown.png"
    zoom 0.815
image helena opensmile blush:
    "images/helena/helena_opensmile_blush.png"
    zoom 0.815
image helena opensmile closedeyes blush:
    "images/helena/helena_opensmile_closedeyes_blush.png"
    zoom 0.815
image helena opensmile closedeyes:
    "images/helena/helena_opensmile_closedeyes.png"
    zoom 0.815
image helena opensmile:
    "images/helena/helena_opensmile.png"
    zoom 0.815
image helena smile blush:
    "images/helena/helena_smile_blush.png"
    zoom 0.815
image helena smile closedeyes blush:
    "images/helena/helena_smile_closedeyes_blush.png"
    zoom 0.815
image helena smile closedeyes:
    "images/helena/helena_smile_closedeyes.png"
    zoom 0.815
image helena smile:
    "images/helena/helena_smile.png"
    zoom 0.815

image sylvia closed frown blush:
    "images/sylvia/sylvia_closed_frown_blush.png"
    zoom 0.225
image sylvia closed frown:
    "images/sylvia/sylvia_closed_frown.png"
    zoom 0.225
image sylvia closed open blush:
    "images/sylvia/sylvia_closed_open_blush.png"
    zoom 0.225
image sylvia closed open:
    "images/sylvia/sylvia_closed_open.png"
    zoom 0.225
image sylvia closed smile blush:
    "images/sylvia/sylvia_closed_smile_blush.png"
    zoom 0.225
image sylvia closed smile:
    "images/sylvia/sylvia_closed_smile.png"
    zoom 0.225
image sylvia frown blush:
    "images/sylvia/sylvia_frown_blush.png"
    zoom 0.225
image sylvia frown:
    "images/sylvia/sylvia_frown.png"
    zoom 0.225
image sylvia open blush:
    "images/sylvia/sylvia_open_blush.png"
    zoom 0.225
image sylvia open:
    "images/sylvia/sylvia_open.png"
    zoom 0.225
image sylvia smile blush:
    "images/sylvia/sylvia_smile_blush.png"
    zoom 0.225
image sylvia smile:
    "images/sylvia/sylvia_smile.png"
    zoom 0.225

image bg drafting = "images/bg/drafting.jpg"
image bg literature = "images/bg/literature.jpg"
image bg literature_2 = "images/bg/literature_2.jpg"
image bg music = "images/bg/music.jpg"
image bg music_2 = "images/bg/music_2.webp"
image bg workshop = "images/bg/workshop.jpg"
image bg workshop_2 = "images/bg/workshop_2.jpg"

init 10 python:
    def _register_location_bgs():
        base = "images/bg/locations/"
        locations = {
            "school_board_office": "student_council_room.png",
            "school_board_office_2": "student_council_room.png",
            "street": "school_street.png",
            "gym": "gymnasium.png",
            "gym_2": "gymnasium.png",
            "locker_room": "girls_locker_room.png",
            "wardrobe": "coatroom.png",
            "corridor": "corridor.png",
            "corridor_2": "corridor.png",
            "assembly_hall": "auditorium.png",
            "assembly_hall_2": "auditorium.png",
            "theater_room": "theater_club.png",
            "theater_room_2": "theater_club.png",
            "theater_room_3": "theater_club.png",
            "storage_room": "backstage_storage.png",
            "storage_room_2": "backstage_storage.png",
            "biology": "biology_classroom.png",
            "laboratory": "biology_prep_lab.png",
            "chemistry_laboratory": "chemistry_prep_lab.png",
            "women_toilet": "girls_restroom.png",
            "men_toilet": "boys_restroom.png",
            "guard_post": "security_post.png",
            "archive": "archive.png",
            "archive_2": "archive.png",
            "generator_room": "generator_room.png",
            "medbay": "infirmary.png",
            "medbay_2": "infirmary.png",
            "robotics": "robotics_club.png",
            "math": "mathematics_classroom.png",
            "teachers_lounge": "staff_room.png",
            "cafeteria": "cafeteria.png",
            "reception": "reception_office.png",
            "psychologist": "psychologist_room.png",
            "physics": "physics_classroom.png",
            "chemistry": "chemistry_classroom.png",
            "library": "library.png",
            "reading_room": "reading_room.png",
            "geography": "geography_classroom.png",
            "journalism": "journalism_club.png",
            "informatics": "computer_classroom.png",
            "rest_room": "lounge.png",
            "social_studies": "social_studies_classroom.png",
            "history": "history_classroom.png",
            "janitor": "janitor_closet.png",
            "principal_office": "principal_office.png",
        }
        for tag, filename in locations.items():
            path = base + filename
            width, height = renpy.image_size(path)
            zoom = max(config.screen_width * 1.0 / width, config.screen_height * 1.0 / height)
            renpy.image("bg " + tag, Transform(path, zoom=zoom))
    _register_location_bgs()
    del _register_location_bgs

