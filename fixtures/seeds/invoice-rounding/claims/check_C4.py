from invoice import *


def test_claim_C4():
    assert format_cents(-1) == '-0.01'
    assert format_cents(120) == '1.20'
