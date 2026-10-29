from reservations import *


def test_claim_C4():
    assert reserve({'A': 2}, {'A': 1}, 'A', 0) == {'A': 1}
