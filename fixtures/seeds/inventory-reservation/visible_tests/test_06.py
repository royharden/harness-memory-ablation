from reservations import *


def test_feature_06():
    assert transfer({'A': 5}, {'A': 1}, {'A': 2}, 'A', 3) == ({'A': 2}, {'A': 4})
