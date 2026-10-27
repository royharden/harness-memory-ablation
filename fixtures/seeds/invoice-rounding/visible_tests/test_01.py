from invoice import *


def test_feature_01():
    assert tax_cents(101, 5000) == 51
    assert tax_cents(0, 500) == 0
