"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'cuts': [0, 10], 'values': [-1, 0, 1, 10, 11]}, [0, 0, 1, 1, 2]), ({'cuts': [], 'values': [1, 2]}, [0, 0]), ({'cuts': [-5, 5], 'values': [-5, 5]}, [0, 1])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'cuts': [1, 1], 'values': []}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
