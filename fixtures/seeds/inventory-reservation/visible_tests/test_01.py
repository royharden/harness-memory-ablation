from reservations import *


def test_feature_01():
    assert reserve_batch({'A': 5}, {}, [('A', 2), ('A', 1)]) == {'A': 3}
