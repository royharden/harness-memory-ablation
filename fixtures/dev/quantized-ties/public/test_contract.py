"""Builder-authored dev expectations; not independent; NOT_RUN."""
import copy
import unittest
from core import solve

CASES = [({'values': [2, 8], 'step': 10}, [0, 10])]


class ContractCases(unittest.TestCase):
    def test_examples_and_input_ownership(self):
        for data, expected in CASES:
            with self.subTest(data=data):
                before = copy.deepcopy(data)
                self.assertEqual(solve(data), expected)
                self.assertEqual(data, before)


if __name__ == "__main__":
    unittest.main()
