from reservations import *


def test_feature_11():
    assert audit_transition({'A': 5}, {'A': 2}, {'A': 4}, {'A': 1}) == (('A', -1, -1, 0),)
