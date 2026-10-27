from reservations import *


def test_feature_09():
    assert shortage({'A': 4}, {'A': 1}, [('A', 2), ('A', 3)]) == (('A', 2),)
