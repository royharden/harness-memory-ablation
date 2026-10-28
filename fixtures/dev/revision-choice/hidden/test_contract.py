"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [([], {}), ([{'key': 'x', 'revision': 2, 'value': 'first'}, {'key': 'x', 'revision': 2, 'value': 'last'}], {'x': 'first'}), ([{'key': 'x', 'revision': 3, 'value': 0}, {'key': 'x', 'revision': 1, 'value': 1}], {'x': 0}), ([{'key': 'a', 'revision': -1, 'value': None}, {'key': 'b', 'revision': 0, 'value': False}], {'a': None, 'b': False})]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [[{'key': 'a', 'revision': True, 'value': 1}]]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
