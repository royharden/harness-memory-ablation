from invoice import *


def test_feature_11():
    assert reconcile(100, [120, -20]) == {'outstanding': 0, 'settled': True}
