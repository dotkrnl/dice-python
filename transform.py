import random # for probabilistic choices
import inspect # used to get the evaluate function source code as a string so the ast module can parse that string
import ast # python's abstract syntax tree library - used to parse function source code to retrieve AST nodes, etc
import numbers # to see if weight values are integers
import subprocess # for routing Dice output to Python program
import sys # for routing Dice output to Python program

global totalDice
totalDice = ""

# go through Python return statement text, parse the logical operators and change them to the Dice equivalent notation ||, &&, !
def translateReturn(returnStatement):
    result = ""

    # split by whitespace: "or" and "and" Python operators are always separated by whitespace
    text = returnStatement.split(" ")
    # print(text)

    # note - still keep any newlines (\n) in result for now, don't think it matters in Dice
    for textSegment in text:
        if "" != textSegment:
            if "or" == textSegment:
                result += " || "
            elif "and" == textSegment:
                result += " && "
            elif ("not" == textSegment):
                result += "!"
            elif ("(not" == textSegment): # this happens if you start an expression with an open parentheses and have a "not" right after that
                result += "(!"
            else:
                result += textSegment
    
    global totalDice
    totalDice += result

class NodeVisitor(ast.NodeVisitor): # child class of ast.NodeVisitor

    def visit_FunctionDef(self, functionDefNode):
        for bodyNode in functionDefNode.body:
            vars = [] # holds variables that we need to define in Dice
            values = [] # holds the value for each of the variable's weights in the vars list

            if isinstance(bodyNode, ast.Assign):
                # for every target (vars that are being assigned), if that target is a Name, and that Name also is a Store (we don't want a Load),
                # then we want to record that target so we can use it in our transformation to Dice code
                for target in bodyNode.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(target.ctx, ast.Store):
                            vars.append(target.id)
                
                # for the one value node, record that value so we can use it in our transformation to Dice code
                valueNode = bodyNode.value
                if isinstance(valueNode, ast.Call):
                    funcNode = valueNode.func
                    argsNode = valueNode.args
                    keywordsNode = valueNode.keywords

                    isRandomChoices = False
                    # check if the funcNode is "random.choices"
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
                            if ((isinstance(keyword, ast.keyword)) and ("weights" == keyword.arg)):
                                if ((isinstance(keyword.value, ast.List)) and (isinstance(keyword.value.ctx, ast.Load))):
                                    weight = keyword.value.elts[0].n
                                    weight /= 10 # to convert to probability
                                    
                                    for var in vars:
                                        global totalDice
                                        totalDice += "let " + var + " = flip " + str(weight) + " in "

            elif isinstance(bodyNode, ast.If):
                super().visit(bodyNode)
            elif isinstance(bodyNode, ast.Return):
                super().visit(bodyNode)

    #def visit_If(self, ifNode):
        #ifCondition = ifNode.test
        #ifBody = ifNode.body
        #restOfIf = ifNode.orelse

        #ifConditionStr = ast.unparse(ifCondition)
        #print("ifCondition: ", ifConditionStr)

    def visit_Return(self, returnNode):
        returnValue = returnNode.value
        returnValueStr = ast.unparse(returnValue)

        # parse and transform return expression (if there is any) to Dice equivalent
        translateReturn(returnValueStr)

def dice(func):
    def wrapper():
        # get source code of function as a string, parse that string to get an AST with AST nodes
        functionSourceCode = inspect.getsource(func)
        #print(functionSourceCode)
        tree = ast.parse(functionSourceCode)
        #print(ast.dump(tree, indent=4))

        # get variables and their corresponding weights from the AST
        NodeVisitor().visit(tree)
        print(totalDice)

        # now have converted Dice code in one string - put it into a new Dice file "translated.dice"
        with open("translated.dice", "w") as file:
            file.write(totalDice)
        
        # now that we can have the translated Python code in translated.dice, we need to run translated.dice using the Dice executable and redirect its output back to Python
        resultExecuted = subprocess.run(["dice", "translated.dice"], capture_output=True)
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
        return diceResult

    return wrapper

# note - the 2 comments below is just conceptually saying how decorators work
# var = decorator(function)
# evaluate = dice(evaluate)
@dice
def evaluate():
    a = random.choices([True, False], weights=[3, 7])
    b = random.choices([True, False], weights=[6, 4])
    c = random.choices([True, False], weights=[1, 9])
    d = random.choices([True, False], weights=[8, 2])
    e = random.choices([True, False], weights=[4, 6])
    return ((a or b or not c) and (b or c or d or not e) and (not b or not d or e) and (not a or not b))

def main():
    result = evaluate()
    print(result)

if __name__ == "__main__":
    main()
