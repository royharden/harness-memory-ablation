"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'values': [], 'width': 2}, []), ({'values': [5, 1, 2, 0], 'width': 2}, [5, 5, 2, 2]), ({'values': [-4, -8, -3], 'width': 8}, [-4, -4, -3]), ({'values': [4, 1, 3], 'width': 1}, [4, 1, 3])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'values': [1], 'width': 0}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
