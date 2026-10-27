from reservations import *


def test_feature_03():
    assert fulfill({'A': 5}, {'A': 3}, 'A', 2) == ({'A': 3}, {'A': 1})
