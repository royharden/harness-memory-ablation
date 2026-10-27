"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'rows': 3, 'cols': 3, 'row': 1, 'col': 1}, [[1, 0], [0, 1], [1, 2], [2, 1]]), ({'rows': 2, 'cols': 2, 'row': 0, 'col': 0}, [[0, 1], [1, 0]]), ({'rows': 1, 'cols': 1, 'row': 0, 'col': 0}, []), ({'rows': 2, 'cols': 3, 'row': 1, 'col': 2}, [[1, 1], [0, 2]])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'rows': 1, 'cols': 1, 'row': 1, 'col': 0}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
