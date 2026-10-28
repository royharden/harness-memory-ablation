from invoice import *


def test_claim_C3():
    try:
        line_total('-0.01', 1)
    except ValueError:
        pass
    else:
        raise AssertionError('negative price accepted')
