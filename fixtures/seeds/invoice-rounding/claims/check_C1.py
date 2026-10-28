from invoice import *


def test_claim_C1():
    assert line_total('0.005', 2) == 1
    assert line_total('0.005', 1) == 1
