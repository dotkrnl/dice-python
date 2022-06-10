from dice import dice, sample
import random


# To use sampling method
#@sample(1000, timed=True)
@dice(timed=True)
def evaluate():
  # example 1: testing random.choices assignments
  a = random.choices([True, False], weights=[3, 7])[0]
  b = random.choices([True, False], weights=[6, 4])[0]
  c = random.choices([True, False], weights=[1, 9])[0]
  d = random.choices([True, False], weights=[8, 2])[0]
  e = random.choices([True, False], weights=[4, 6])[0]
  return ((a or b or not c) and (b or c or d or not e) and
          (not b or not d or e) and (not a or not b))

  ''' # example 2: testing basic if/else functionality
    b = random.choices([True, False], weights=[3, 7])[0]
    if b:
        a = random.choices([True, False], weights=[3, 7])[0]
    else:
        a = random.choices([True, False], weights=[2, 8])[0]
    result = b or a
    if result:
        return b
    return result
    '''

  ''' # example 3: testing basic if/elif/else functionality
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
    '''

  ''' # example 4: testing nested if's
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
    '''

  ''' # example 5: testing different ordering of example 4
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
    '''
    
  ''' # example 6: testing different ordering of example 5
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
    '''


def main():
  result = evaluate()
  print(result)


if __name__ == "__main__":
  main()
