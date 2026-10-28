"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'graph': {'s': ['a', 'b'], 'a': ['c'], 'b': ['c'], 'c': []}, 'start': 's'}, ['s', 'b', 'a', 'c']), ({'graph': {'x': ['x']}, 'start': 'x'}, ['x']), ({'graph': {'a': ['b', 'b'], 'b': [], 'z': []}, 'start': 'a'}, ['a', 'b'])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'graph': {'a': ['b']}, 'start': 'a'}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
