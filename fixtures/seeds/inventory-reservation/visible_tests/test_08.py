from reservations import *


def test_feature_08():
    assert expire_holds([('h1', 'A', 2, 5), ('h2', 'A', 1, 6)], 5) == ((('h2', 'A', 1, 6),), {'A': 2})
