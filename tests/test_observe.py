import unittest

from dice import dice, sample
import random


def evaluate():
  burglary = random.choices([True, False], weights=[1, 999])[0]

  if burglary:
    alarm = random.choices([True, False], weights=[95, 5])[0]
  else:
    alarm = random.choices([True, False], weights=[1, 999])[0]

  return burglary


class TestObserve(unittest.TestCase):

  @unittest.skip('dice bug')
  def test_single_dice(self):
    result = dice()(evaluate).observe(
        'alarm', True)()
    self.assertAlmostEqual(result[True], 0.913461538462)
    self.assertAlmostEqual(result[False], 0.0865384615385)


if __name__ == '__main__':
  unittest.main()
