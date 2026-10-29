"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'x': 2, 'terms': [[0, 3], [2, 4], [2, -1]]}, 15), ({'x': 0, 'terms': [[0, 7], [2, 4]]}, 7), ({'x': -2, 'terms': [[3, 2], [1, 3]]}, -22), ({'x': 3, 'terms': []}, 0)]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'x': 2, 'terms': [[-1, 1]]}, {'x': True, 'terms': []}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
