from invoice import *


def test_feature_05():
    assert decode_lines(encode_lines([('1.005', 2)])) == (['1.005', 2],)
