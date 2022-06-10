import unittest

from dice import dice, sample
import random


def evaluate():
  a = random.choices([True, False], weights=[4, 6])[0]
  b = random.choices([True, False], weights=[3, 7])[0]
  if a:
    c = random.choices([True, False], weights=[2, 8])[0]
  elif b:
    c = random.choices([True, False], weights=[1, 9])[0]
  else:
    c = random.choices([True, False], weights=[3, 7])[0]
  result = a and b and c
  if result:
    return c
  return result


class TestIfElifElse(unittest.TestCase):

  def test_single_dice(self):
    result = dice()(evaluate)()
    self.assertAlmostEqual(result[True], 0.024)
    self.assertAlmostEqual(result[False], 0.976)

  def test_single_sample(self):
    result = sample(100000)(evaluate)()
    self.assertAlmostEqual(result[True], 0.024, 1)
    self.assertAlmostEqual(result[False], 0.976, 1)


if __name__ == '__main__':
  unittest.main()
