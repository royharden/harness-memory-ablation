from reservations import *


def test_claim_C2():
    try:
        reserve({'A': 2}, {'A': 1}, 'A', 2)
    except ValueError:
        pass
    else:
        raise AssertionError('oversell accepted')
