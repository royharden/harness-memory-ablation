from reservations import *


def test_baseline_B4():
    assert reserve({'A': 2}, {'A': 1}, 'A', 0) == {'A': 1}
