"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'base': {}, 'edits': []}, {}), ({'base': {'a': 1}, 'edits': [['a', None], ['b', 0]]}, {'b': 0}), ({'base': {}, 'edits': [['x', 1], ['x', 2], ['z', None]]}, {'x': 2}), ({'base': {'a': 2}, 'edits': [['a', False]]}, {'a': False})]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'base': {}, 'edits': [['x']]}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
