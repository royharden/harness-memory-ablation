from invoice import *


def test_feature_08():
    assert group_totals([('USD', [('1', 1)]), ('EUR', [('2', 1)]), ('USD', [])]) == (('EUR', 200), ('USD', 100))
