from reservations import *


def test_feature_02():
    assert release_batch({'A': 5}, [('A', 1), ('A', 2)]) == {'A': 2}
