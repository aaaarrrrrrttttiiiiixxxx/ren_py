## Fixture for the playthrough harness self-test
## (playthrough::_selftest_overlap_detected). Shows two girls on the same slot
## on purpose; the harness must report a violation.

label _overlap_self_test:
    scene black
    show alice smile at left
    show mari smile at left
    n "overlap on purpose"
    return
