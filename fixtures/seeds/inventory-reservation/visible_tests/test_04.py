from reservations import *


def test_feature_04():
    assert restock({'A': 2}, {'A': 3, 'B': 1}) == {'A': 5, 'B': 1}
