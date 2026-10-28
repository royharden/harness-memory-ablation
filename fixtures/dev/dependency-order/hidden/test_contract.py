"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({}, []), ({'b': [], 'a': []}, ['a', 'b']), ({'a': ['b', 'b'], 'b': [], 'c': []}, ['b', 'a', 'c']), ({'x': ['y'], 'y': ['z'], 'z': []}, ['z', 'y', 'x'])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in [{'a': ['b']}, {'a': ['a']}]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
