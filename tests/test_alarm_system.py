import unittest

from dice import dice, sample
import random


def evaluate():
  burglary = random.choices([True, False], weights=[1, 999])[0]
  earthquake = random.choices([True, False], weights=[2, 998])[0]

  if burglary and earthquake:
    alarm = random.choices([True, False], weights=[95, 5])[0]
  elif burglary and not earthquake:
    alarm = random.choices([True, False], weights=[94, 6])[0]
  elif not burglary and earthquake:
    alarm = random.choices([True, False], weights=[29, 71])[0]
  else:
    alarm = random.choices([True, False], weights=[1, 999])[0]

  if alarm:
    johncalls = random.choices([True, False], weights=[90, 10])[0]
    marycalls = random.choices([True, False], weights=[70, 30])[0]
  else:
    johncalls = random.choices([True, False], weights=[5, 95])[0]
    marycalls = random.choices([True, False], weights=[1, 99])[0]

  return burglary or earthquake


class TestAlarmSystem(unittest.TestCase):

  @unittest.skip('dice bug')
  def test_single_dice(self):
    result = dice()(evaluate).observe(
        'johncalls', True).observe(
        'marycalls', True)()
    self.assertAlmostEqual(result[True], 0.459664301204)
    self.assertAlmostEqual(result[False], 0.5403356988)


if __name__ == '__main__':
  unittest.main()
