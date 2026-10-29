from invoice import *


def test_feature_09():
    assert installment_plan(10, 3) == (4, 3, 3)
    assert installment_plan(0, 2) == (0, 0)
