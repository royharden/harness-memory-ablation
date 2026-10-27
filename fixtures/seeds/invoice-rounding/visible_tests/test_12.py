from invoice import *


def test_feature_12():
    assert batch_summary([{'lines': [('1', 2)], 'discount': 50, 'tax_basis_points': 1000}]) == {'count': 1, 'subtotal': 200, 'discount': 50, 'tax': 15, 'total': 165}
