import unittest

from dice import dice, sample
import random

def evaluate():
    b = random.choices([True, False], weights=[3, 7])[0]
    if b:
        a = random.choices([True, False], weights=[3, 7])[0]
    else:
        a = random.choices([True, False], weights=[2, 8])[0]
    result = b or a
    if result:
        return b
    else:
        return result
        a = False

class TestIfElseReturn(unittest.TestCase):

    def test_single_dice(self):
        result = dice()(evaluate)()
        self.assertAlmostEqual(result[True], 0.3)
        self.assertAlmostEqual(result[False], 0.7)

    def test_single_sample(self):
        result = sample(100000)(evaluate)()
        self.assertAlmostEqual(result[True], 0.3, 1)
        self.assertAlmostEqual(result[False], 0.7, 1)

if __name__ == '__main__':
    unittest.main()