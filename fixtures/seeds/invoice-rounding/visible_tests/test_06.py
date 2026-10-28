from invoice import *


def test_feature_06():
    assert [r['total'] for r in quote_batch([{'lines': [('1', 1)]}, {'lines': []}])] == [100, 0]
