from invoice import *


def test_feature_10():
    assert progressive_total(5, [(3, '1.00'), (10, '0.50')]) == 400
