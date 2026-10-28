from reservations import *


def test_feature_10():
    assert rebalance({'A': 5}, {'A': 2}, {'A': 1, 'B': 2}) == (('A', -2), ('B', 2))
