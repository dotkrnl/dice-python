import random # for probabilistic choices
import inspect # used to get the evaluate function source code as a string so the ast module can parse that string
import ast # python's abstract syntax tree library - used to parse function source code to retrieve AST nodes, etc
import numbers # to see if weight values are integers
import subprocess # for routing Dice output to Python program
import sys # for routing Dice output to Python program

varsToWeights = {} # dictionary where keys are variables and values are that variables' associated weights

def translateVarsAndWeights(mapping):
    result = []
    for var in mapping:
        weights = mapping[var]
        # only need one weight for Dice "flip", just get the first one
        flipWeight = weights[0]
        result.append("let " + var + " = flip " + str(flipWeight) + " in ")
    return result


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
    
    return result

# todo: have to visit function definition first - then inside that visit the assign node, 
# otherwise it skips the Assign node since the Assign node is within the body of the function definition node
class NodeTransformer(ast.NodeTransformer): # child class of ast.NodeTransformer

    def visit_FunctionDef(self, functionDefNode):
        for bodyNode in functionDefNode.body:
            vars = [] # holds variables that we need to define in Dice
            values = [] # holds the value for each of the variable's weights in the vars list

            if isinstance(bodyNode, ast.Assign):
                # for every target (vars that are being assigned), if that target is a Name, and that Name also is a Store (and not a Load),
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
                                    for element in keyword.value.elts:
                                        if isinstance(element, ast.Num) and isinstance(element.n, numbers.Integral):
                                            # check to see if weight values are unsigned ints
                                            if element.n > 0:
                                                values.append(element.n)
        
            # divide by 10 to get probabilities
            for i in range(len(values)):
                values[i] /= 10

            # add (var, [weights]) to dict as a key, value pair
            for var in vars:
                varsToWeights[var] = values
    


def dice(func):
    def wrapper():
        # get source code of function as a string, parse that string to get an AST with AST nodes
        functionSourceCode = inspect.getsource(func)
        #print(functionSourceCode)
        tree = ast.parse(functionSourceCode)
        #print(ast.dump(tree, indent=4))

        # get variables and their corresponding weights from the AST
        NodeTransformer().visit(tree)
        print(varsToWeights)

        # transform mapping of variables and their corresponding weights to Dice equivalent, put each local var as element in array
        diceLocalVars = translateVarsAndWeights(varsToWeights)
        print(diceLocalVars)

        # combine elements of local var array together into one string
        diceVarString = ""
        for localVar in diceLocalVars:
            diceVarString += localVar
        print(diceVarString)

        # parse and transform return expression (if there is any) to Dice equivalent
        returnStatement = functionSourceCode.split("return", 1)[1]
        diceReturnExpression = translateReturn(returnStatement)
        print(diceReturnExpression)

        # We have translated Dice code of mapping of vars to weights and translated Dice code for return statement
        # Now, just combine them together
        diceCode = diceVarString + diceReturnExpression
        print(diceCode)

        # now have converted Dice code in one string - put it into a new Dice file "translated.dice"
        with open("translated.dice", "w") as file:
            file.write(diceCode)
        
        # now that we can run that translated.dice code succesfully in Dice, we need to redirect its output back to Python
        # note - this hasn't been tested yet - can't get Dice correctly installed on my virtual machine so far
        resultExecuted = subprocess.run(["dice", "translated.dice"], capture_output=True)
        diceResultString = str(resultExecuted.stdout, "utf-8")
        # split stdout string to find true and false values
        splitTrue = diceResultString.split("true", 1)[1]
        splitFalse = splitTrue.split("false", 1)
        trueVal = float(splitFalse[0])
        falseVal = float(splitFalse[1])

        """ sampleString = "Value Probability true 0.348837 false 0.651163" # just for testing right now since subprocess stuff I can't test as of now
        splitTrue = sampleString.split("true", 1)[1]
        splitFalse = splitTrue.split("false", 1)
        trueVal = float(splitFalse[0])
        falseVal = float(splitFalse[1]) """

        # add mappings to the diceResult dictionary to return to the user
        diceResult = {} # dictionary that contains the final evaluated output that was executed in Dice
        diceResult[True] = trueVal
        diceResult[False] = falseVal
        return diceResult

    return wrapper

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
