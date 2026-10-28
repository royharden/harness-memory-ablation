from reservations import *


def test_feature_05():
    assert decode_state(encode_state({'A': 5}, {'A': 2})) == ({'A': 5}, {'A': 2})
