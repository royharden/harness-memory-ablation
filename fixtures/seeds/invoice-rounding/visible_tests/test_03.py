from invoice import *


def test_feature_03():
    assert split_charge(5, [1, 1, 1]) == (2, 2, 1)
    assert split_charge(1, [0, 2]) == (0, 1)
