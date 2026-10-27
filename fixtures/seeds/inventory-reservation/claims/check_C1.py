from reservations import *


def test_claim_C1():
    original = {'A': 1}
    assert reserve({'A': 5}, original, 'A', 2) == {'A': 3}
    assert original == {'A': 1}
