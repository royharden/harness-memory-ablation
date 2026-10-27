from reservations import *


def test_feature_12():
    assert apply_operations({'A': 2}, {}, [{'kind': 'reserve', 'sku': 'A', 'quantity': 2}, {'kind': 'fulfill', 'sku': 'A', 'quantity': 1}]) == ({'A': 1}, {'A': 1})
