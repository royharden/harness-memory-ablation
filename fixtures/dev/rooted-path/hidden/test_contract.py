"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [('/a//b/../c/', '/a/c'), ('/', '/'), ('/a/..././', '/a/...'), ('/a/../', '/')]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)

    def test_invalid_input(self):
        for data in ['/../a', '/a/../../x', 'relative']:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solve(data)


if __name__ == "__main__":
    unittest.main()
