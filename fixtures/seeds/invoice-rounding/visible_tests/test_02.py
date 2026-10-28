from invoice import *


def test_feature_02():
    assert discounted(101, 1) == 100
    assert discounted(10, 10) == 0
