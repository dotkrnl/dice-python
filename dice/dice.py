from . import ast as dice_ast

# used to get the evaluate function source code as a string so the ast
# module can parse that string
import inspect
# python's abstract syntax tree library - used to parse function source
# code to retrieve AST nodes, etc
import ast
# for routing Dice output to Python program
import subprocess
import time


class DiceCallable:
  def __init__(self, timed, func):
    self.timed = timed
    self.func = func
    self.visitor = dice_ast.DiceVisitor()

  def __call__(self):
    # get source code of function as a string, parse that string to get
    # an AST with AST nodes
    functionSourceCode = inspect.getsource(self.func)
    tree = ast.parse(functionSourceCode)

    # get variables and their corresponding weights from the AST
    self.visitor.visit(tree)
    totalDice = self.visitor.get_program()

    # now have converted Dice code in one string - put it into a Dice file
    with open("translated.dice", "w") as file:
      file.write(totalDice)

    # now that we can have the translated Python code, we need to run using
    # the Dice executable and redirect its output back to Python
    startTime = time.time()
    resultExecuted = subprocess.run(
        ["dice", "translated.dice"],
        capture_output=True)
    endTime = time.time()
    timeDifference = endTime - startTime

    diceErrorString = str(resultExecuted.stderr, "utf-8")
    if diceErrorString:
      print(diceErrorString)

    diceResultString = str(resultExecuted.stdout, "utf-8")
    # diceResultString is of the form:
    # =============[Joint Distribution]===============
    # Value     Probability
    # true      0.5616
    # false     0.4384

    # split stdout string to find true and false values
    splitTrue = diceResultString.split("true", 1)[1]
    splitFalse = splitTrue.split("false", 1)
    trueVal = float(splitFalse[0])
    falseVal = float(splitFalse[1])

    # add mappings to the diceResult dictionary to return to the user
    diceResult = {}
    diceResult[True] = trueVal
    diceResult[False] = falseVal

    if self.timed:
      diceResult["Time"] = timeDifference

    return diceResult

  def observe(self, var, val):
    self.visitor.observe(var, val)
    return self


def dice(timed=False):
  def decorator(func):
    return DiceCallable(timed, func)
  return decorator


def sample(n, timed=False):
  def decorator(func):
    def wrapper():
      sampleResult = {}

      startTime = time.time()
      for _ in range(n):
        result = func()
        sampleResult[result] = sampleResult.get(result, 0) + 1./n
      endTime = time.time()
      timeDifference = endTime - startTime

      if timed:
        sampleResult["Time"] = timeDifference

      return sampleResult

    return wrapper

  return decorator
