import unittest

from dice import dice, sample
import random


def evaluate():
  a = random.choices([True, False], weights=[3, 7])[0]
  b = random.choices([True, False], weights=[6, 4])[0]
  c = random.choices([True, False], weights=[1, 9])[0]
  d = random.choices([True, False], weights=[8, 2])[0]
  e = random.choices([True, False], weights=[4, 6])[0]
  return ((a or b or not c) and (b or c or d or not e) and
          (not b or not d or e) and (not a or not b))


class TestRandomChoices(unittest.TestCase):

  def test_single_dice(self):
    result = dice()(evaluate)()
    self.assertAlmostEqual(result[True], 0.5616)
    self.assertAlmostEqual(result[False], 0.4384)

  def test_single_sample(self):
    result = sample(100000)(evaluate)()
    self.assertAlmostEqual(result[True], 0.5616, 1)
    self.assertAlmostEqual(result[False], 0.4384, 1)


if __name__ == '__main__':
  unittest.main()
