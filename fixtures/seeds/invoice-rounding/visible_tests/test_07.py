from invoice import *


def test_feature_07():
    assert credit_balance(100, [30, 90]) == {'due': 0, 'unused': 20}
