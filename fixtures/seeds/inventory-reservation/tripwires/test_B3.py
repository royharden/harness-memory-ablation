from reservations import *


def test_baseline_B3():
    assert available({}, {}, 'missing') == 0
