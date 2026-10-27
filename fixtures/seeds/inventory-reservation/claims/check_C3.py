from reservations import *


def test_claim_C3():
    assert available({}, {}, 'missing') == 0
