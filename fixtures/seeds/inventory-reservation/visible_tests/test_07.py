from reservations import *


def test_feature_07():
    assert allocate_orders({'A': 3}, {}, [[('A', 2)], [('A', 2)], [('A', 1)]]) == ({'A': 3}, (True, False, True))
