from . import ast as dice_ast

import inspect # used to get the evaluate function source code as a string so the ast module can parse that string
import ast # python's abstract syntax tree library - used to parse function source code to retrieve AST nodes, etc
import subprocess # for routing Dice output to Python program
import time # for timing

def dice(timed=False):
    def decorator(func):
        def wrapper():
            # get source code of function as a string, parse that string to get an AST with AST nodes
            functionSourceCode = inspect.getsource(func)
            #print(functionSourceCode)
            tree = ast.parse(functionSourceCode)
            #print(ast.dump(tree, indent=4))

            # get variables and their corresponding weights from the AST
            visitor = dice_ast.DiceVisitor()
            visitor.visit(tree)
            totalDice = visitor.get_program()

            # now have converted Dice code in one string - put it into a new Dice file "translated.dice"
            with open("translated.dice", "w") as file:
                file.write(totalDice)
            
            # now that we can have the translated Python code in translated.dice, we need to run translated.dice using the Dice executable and redirect its output back to Python
            startTime = time.time()
            resultExecuted = subprocess.run(["dice", "translated.dice"], capture_output=True)
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
            diceResult = {} # dictionary that contains the final evaluated output that was executed in Dice
            diceResult[True] = trueVal
            diceResult[False] = falseVal

            if timed:
                diceResult["Time"] = timeDifference

            return diceResult

        return wrapper

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