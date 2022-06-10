import random # for probabilistic choices
import inspect # used to get the evaluate function source code as a string so the ast module can parse that string
import ast # python's abstract syntax tree library - used to parse function source code to retrieve AST nodes, etc
import numbers # to see if weight values are integers
import subprocess # for routing Dice output to Python program
import sys # for routing Dice output to Python program
import time # for timing

global totalDice
totalDice = ""

global lastStatementInIf
lastStatementInIf = False

global numberOfIfs
numberOfIfs = 0

def translateBooleanExpression(textWhitespace):
    diceBooleanExp = ""

    # split by whitespace: "or" and "and" Python operators are always separated by whitespace
    text = textWhitespace.split(" ")

    # note - still keep any newlines (\n) in result for now, don't think it matters in Dice
    for textSegment in text:
        if "" != textSegment:
            if "or" == textSegment:
                diceBooleanExp += " || "
            elif "and" == textSegment:
                diceBooleanExp += " && "
            elif ("not" == textSegment):
                diceBooleanExp += "!"
            elif ("(not" == textSegment): # this happens if you start an expression with an open parentheses and have a "not" right after that
                diceBooleanExp += "(!"
            elif ("True" == textSegment):
                diceBooleanExp += "true"
            elif ("False" == textSegment):
                diceBooleanExp += "false"
            elif (">=" == textSegment):
                diceBooleanExp += " >= "
            elif ("<=" == textSegment):
                diceBooleanExp += " <= "
            elif ("!=" == textSegment):
                diceBooleanExp += " != "
            elif ("==" == textSegment):
                diceBooleanExp += " == "
            else:
                diceBooleanExp += textSegment

    return diceBooleanExp
                
def isAssignRandomChoice(assignNode):
    global totalDice
    global lastStatementInIf

    vars = [] # holds variables that we need to define in Dice

    # for every target (vars that are being assigned), if that target is a Name, and that Name also is a Store (we don't want a Load),
    # then we want to record that target so we can use it in our transformation to Dice code
    for target in assignNode.targets:
        if isinstance(target, ast.Name):
            if isinstance(target.ctx, ast.Store):
                vars.append(target.id)

    # for the one value node, record that value so we can use it in our transformation to Dice code
    valueNode = assignNode.value
    if isinstance(valueNode, ast.Call):
        funcNode = valueNode.func
        argsNode = valueNode.args
        keywordsNode = valueNode.keywords

        isRandomChoices = False
        # check if the funcNode is "random.chioces"
        if (isinstance(funcNode, ast.Attribute)) and ("choices" == funcNode.attr):
            if isinstance(funcNode.value, ast.Name):
                nameNode = funcNode.value
                if ("random" == nameNode.id) and (isinstance(nameNode.ctx, ast.Load)):
                    isRandomChoices = True

        isTrueOrFalseConstants = False
        if isRandomChoices:
            # check if arguments are True or False constants
            for args in argsNode:
                if (isinstance(args, ast.List)) and (isinstance(args.ctx, ast.Load)):
                    for argument in args.elts:
                        if ((isinstance(argument, ast.NameConstant)) and (True == argument.value or False == argument.value)):
                            isTrueOrFalseConstants = True

        if isTrueOrFalseConstants:
            # check if weights are valid
            for keyword in keywordsNode:
                if ((isinstance(keyword.value, ast.List)) and (isinstance(keyword.value.ctx, ast.Load))):
                    weight = keyword.value.elts[0].n
                    weight /= 10 # to convert to probability

                    for var in vars:
                        totalDice += "let " + var + " = flip " + str(weight) + " in "

                    # if lastStatementIf is true, need to finish "in" portion
                    if lastStatementInIf and numberOfIfs > 0:
                        lastVar = vars[-1]
                        totalDice += lastVar + " "
                        lastStatementInIf = False

        if isTrueOrFalseConstants:
            return True
        return False

def isAssignBooleanOperation(assignNode):
    global totalDice
    global lastStatementInIf

    vars = []

    for target in assignNode.targets:
        if isinstance(target, ast.Name):
            if isinstance(target.ctx, ast.Store):
                vars.append(target.id)

    valueNode = assignNode.value
    if isinstance(valueNode, ast.BoolOp):
        # don't need "<var =" part of assignment, just need the boolean expression
        booleanExpr = ast.unparse(assignNode).split(vars[-1] + " = ")[1]
        booleanExprStr = translateBooleanExpression(booleanExpr)
        
        for var in vars:
            totalDice += "let " + var + " = " + booleanExprStr + " in "

        if lastStatementInIf:
            lastVar = vars[-1]
            totalDice += lastVar + " "
            lastStatementInIf = False

        return True
    return False

def isAssignConstant(assignNode):
    global totalDice
    global lastStatementInIf

    vars = []

    for target in assignNode.targets:
        if isinstance(target, ast.Name):
            if isinstance(target.ctx, ast.Store):
                vars.append(target.id)

    valueNode = assignNode.value
    if isinstance(valueNode, ast.Constant):
        constantStr = ast.unparse(valueNode)
        diceConstantStr = translateBooleanExpression(constantStr) 

        for var in vars:
            totalDice += "let " + var + " = " + diceConstantStr + " in "

        '''
        if lastStatementInIf:
            lastVar = vars[-1]
            totalDice += lastVar + " "
            lastStatementInIf = False
        '''

        return True
    return False

class NodeVisitor(ast.NodeVisitor): # child class of ast.NodeVisitor

    def visit_FunctionDef(self, functionDefNode):
        for bodyNode in functionDefNode.body:
            super().visit(bodyNode)

    def visit_Assign(self, assignNode):
        global totalDice
        global lastStatementInIf

        if isAssignRandomChoice(assignNode):
            return
        elif isAssignBooleanOperation(assignNode):
            return
        elif isAssignConstant(assignNode):
            return

    def visit_If(self, ifNode):
        global totalDice
        global lastStatementInIf
        global numberOfIfs
        numberOfIfs += 1

        ifCondition = ifNode.test
        ifBody = ifNode.body
        restOfIf = ifNode.orelse

        ifConditionStr = ast.unparse(ifCondition)
        totalDice += "if " + ifConditionStr + " then "
        #print("ifCondition: ", ifConditionStr)

        ifBodyListLength = len(ifBody) - 1
        for node in ifBody:
            if ifBody.index(node) == ifBodyListLength:
                lastStatementInIf = True
            super().visit(node)

        numberOfIfs -= 1
        if (0 == numberOfIfs and 0 == len(restOfIf)):
            totalDice += "else "
        else:
            for node in restOfIf:
                totalDice += "else "
                super().visit(node)

    def visit_Return(self, returnNode):
        global totalDice

        returnValue = returnNode.value
        returnValueStr = ast.unparse(returnValue)
        diceResultExpr = translateBooleanExpression(returnValueStr)

        totalDice += diceResultExpr + " "

def dice(timed=False):
    def decorator(func):
        def wrapper():
            # get source code of function as a string, parse that string to get an AST with AST nodes
            functionSourceCode = inspect.getsource(func)
            #print(functionSourceCode)
            tree = ast.parse(functionSourceCode)
            #print(ast.dump(tree, indent=4))

            # get variables and their corresponding weights from the AST
            NodeVisitor().visit(tree)
            #print(totalDice)

            # now have converted Dice code in one string - put it into a new Dice file "translated.dice"
            with open("translated.dice", "w") as file:
                file.write(totalDice)
            
            # now that we can have the translated Python code in translated.dice, we need to run translated.dice using the Dice executable and redirect its output back to Python
            startTime = time.time()
            resultExecuted = subprocess.run(["dice", "translated.dice"], capture_output=True)
            endTime = time.time()
            timeDifference = endTime - startTime


            diceErrorString = str(resultExecuted.stderr, "utf-8")
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

# note - the 2 comments below is just conceptually saying how decorators work
# var = decorator(function)
# evaluate = dice(evaluate)
@dice(timed=True)
def evaluate():
     # example 1: testing random.choices assignments
    a = random.choices([True, False], weights=[3, 7])
    b = random.choices([True, False], weights=[6, 4])
    c = random.choices([True, False], weights=[1, 9])
    d = random.choices([True, False], weights=[8, 2])
    e = random.choices([True, False], weights=[4, 6])
    return ((a or b or not c) and (b or c or d or not e) and (not b or not d or e) and (not a or not b))
    

    ''' # example 2: testing basic if/else functionality
    b = random.choices([True, False], weights=[3, 7])
    if b:
        a = random.choices([True, False], weights=[3, 7])
    else:
        a = random.choices([True, False], weights=[2, 8])
    result = b or a
    if result:
        return b
    return result
    '''

    ''' # example 3: testing basic if/elif/else functionality
    a = random.choices([True, False], weights=[4, 6])
    b = random.choices([True, False], weights=[3, 7])
    if a:
        c = random.choices([True, False], weights=[2, 8])
    elif b:
        c = random.choices([True, False], weights=[1, 9])
    else:
        c = random.choices([True, False], weights=[3, 7])
    result = a and b and c
    if result:
        return c
    return result
    '''

    ''' # example 4: testing nested if's
    a = random.choices([True, False], weights=[2, 8])
    b = random.choices([True, False], weights=[5, 5])
    c = random.choices([True, False], weights=[7, 3])
    if a:
        if b:
            if c:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])
    return a
    '''

    ''' # example 5: testing different ordering of example 4
    a = random.choices([True, False], weights=[2, 8])
    b = random.choices([True, False], weights=[5, 5])
    c = random.choices([True, False], weights=[7, 3])
    if b:
        if c:
            if a:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])
    return a
    '''

    ''' # example 6: testing different ordering of example 5
    a = random.choices([True, False], weights=[2, 8])
    b = random.choices([True, False], weights=[5, 5])
    c = random.choices([True, False], weights=[7, 3])
    if c:
        if b:
            if a:
                return a
            else:
                return b
        else:
            return c
    else:
        a = random.choices([True, False], weights=[1, 9])
    return a
    '''
    

def main():
    result = evaluate()
    print(result)

if __name__ == "__main__":
    main()
