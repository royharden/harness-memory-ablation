from invoice import *


def test_feature_04():
    assert quote([('1.00', 2)], 50, 1000) == {'subtotal': 200, 'discount': 50, 'tax': 15, 'total': 165}
