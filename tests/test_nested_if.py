import unittest

from dice import dice, sample
import random

def evaluate1():
    a = random.choices([True, False], weights=[2, 8])[0]
    b = random.choices([True, False], weights=[5, 5])[0]
    c = random.choices([True, False], weights=[7, 3])[0]
    if a:
        if b:
            if c:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])[0]
    return a


def evaluate2():
    a = random.choices([True, False], weights=[2, 8])[0]
    b = random.choices([True, False], weights=[5, 5])[0]
    c = random.choices([True, False], weights=[7, 3])[0]
    if b:
        if c:
            if a:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])[0]
    return a

def evaluate3():
    a = random.choices([True, False], weights=[2, 8])[0]
    b = random.choices([True, False], weights=[5, 5])[0]
    c = random.choices([True, False], weights=[7, 3])[0]
    if c:
        if b:
            if a:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])[0]
    return a

class TestNestedIf(unittest.TestCase):

    def test_single_dice1(self):
        result = dice()(evaluate1)()
        self.assertAlmostEqual(result[True], 0.25)
        self.assertAlmostEqual(result[False], 0.75)

    def test_single_sample1(self):
        result = sample(100000)(evaluate1)()
        self.assertAlmostEqual(result[True], 0.25, 1)
        self.assertAlmostEqual(result[False], 0.75, 1)

    def test_single_dice2(self):
        result = dice()(evaluate2)()
        self.assertAlmostEqual(result[True], 0.4)
        self.assertAlmostEqual(result[False], 0.6)

    def test_single_sample2(self):
        result = sample(100000)(evaluate2)()
        self.assertAlmostEqual(result[True], 0.4, 1)
        self.assertAlmostEqual(result[False], 0.6, 1)

    def test_single_dice3(self):
        result = dice()(evaluate3)()
        self.assertAlmostEqual(result[True], 0.73)
        self.assertAlmostEqual(result[False], 0.27)

    def test_single_sample3(self):
        result = sample(100000)(evaluate3)()
        self.assertAlmostEqual(result[True], 0.73, 1)
        self.assertAlmostEqual(result[False], 0.27, 1)

if __name__ == '__main__':
    unittest.main()