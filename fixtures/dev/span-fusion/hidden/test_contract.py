"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [([], []), ([[3, 6], [1, 3], [9, 9], [5, 8]], [[1, 8]]), ([[0, 10], [2, 3], [12, 14]], [[0, 10], [12, 14]]), ([[-4, -2], [-2, 0]], [[-4, 0]])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [[[2, 1]], [[True, 2]]]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
