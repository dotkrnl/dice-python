import ast # python's abstract syntax tree library - used to parse function source code to retrieve AST nodes, etc

class DiceVisitor(ast.NodeVisitor): # child class of ast.NodeVisitor

    totalDice = ""
    lastStatementInIf = False
    numberOfIfs = 0

    def translateBooleanExpression(self, textWhitespace):
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
                    
    def isAssignRandomChoice(self, assignNode):

        vars = [] # holds variables that we need to define in Dice

        # for every target (vars that are being assigned), if that target is a Name, and that Name also is a Store (we don't want a Load),
        # then we want to record that target so we can use it in our transformation to Dice code
        for target in assignNode.targets:
            if isinstance(target, ast.Name):
                if isinstance(target.ctx, ast.Store):
                    vars.append(target.id)

        # for the one value node, record that value so we can use it in our transformation to Dice code
        valueNode = assignNode.value

        # FIXME: if not [0]
        if isinstance(valueNode, ast.Subscript):
            if isinstance(valueNode.slice, ast.Constant):
                if valueNode.slice.value == 0:
                    valueNode = valueNode.value

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
                            self.totalDice += "let " + var + " = flip " + str(weight) + " in "

                        # if lastStatementIf is true, need to finish "in" portion
                        if self.lastStatementInIf and self.numberOfIfs > 0:
                            lastVar = vars[-1]
                            self.totalDice += lastVar + " "
                            self.lastStatementInIf = False

            if isTrueOrFalseConstants:
                return True
            return False

    def isAssignBooleanOperation(self, assignNode):

        vars = []

        for target in assignNode.targets:
            if isinstance(target, ast.Name):
                if isinstance(target.ctx, ast.Store):
                    vars.append(target.id)

        valueNode = assignNode.value
        if isinstance(valueNode, ast.BoolOp):
            # don't need "<var =" part of assignment, just need the boolean expression
            booleanExpr = ast.unparse(assignNode).split(vars[-1] + " = ")[1]
            booleanExprStr = self.translateBooleanExpression(booleanExpr)
            
            for var in vars:
                self.totalDice += "let " + var + " = " + booleanExprStr + " in "

            if self.lastStatementInIf:
                lastVar = vars[-1]
                self.totalDice += lastVar + " "
                self.lastStatementInIf = False

            return True
        return False

    def isAssignConstant(self, assignNode):

        vars = []

        for target in assignNode.targets:
            if isinstance(target, ast.Name):
                if isinstance(target.ctx, ast.Store):
                    vars.append(target.id)

        valueNode = assignNode.value
        if isinstance(valueNode, ast.Constant):
            constantStr = ast.unparse(valueNode)
            diceConstantStr = self.translateBooleanExpression(constantStr) 

            for var in vars:
                self.totalDice += "let " + var + " = " + diceConstantStr + " in "

            '''
            if self.lastStatementInIf:
                lastVar = vars[-1]
                self.totalDice += lastVar + " "
                self.lastStatementInIf = False
            '''

            return True
        return False

    def visit_FunctionDef(self, functionDefNode):
        for bodyNode in functionDefNode.body:
            super().visit(bodyNode)

    def visit_Assign(self, assignNode):

        if self.isAssignRandomChoice(assignNode):
            return
        elif self.isAssignBooleanOperation(assignNode):
            return
        elif self.isAssignConstant(assignNode):
            return

    def visit_If(self, ifNode):
      
        self.numberOfIfs += 1

        ifCondition = ifNode.test
        ifBody = ifNode.body
        restOfIf = ifNode.orelse

        ifConditionStr = ast.unparse(ifCondition)
        self.totalDice += "if " + ifConditionStr + " then "
        #print("ifCondition: ", ifConditionStr)

        ifBodyListLength = len(ifBody) - 1
        for node in ifBody:
            if ifBody.index(node) == ifBodyListLength:
                self.lastStatementInIf = True
            super().visit(node)

        self.numberOfIfs -= 1
        if (0 == self.numberOfIfs and 0 == len(restOfIf)):
            self.totalDice += "else "
        else:
            for node in restOfIf:
                self.totalDice += "else "
                super().visit(node)

    def visit_Return(self, returnNode):

        returnValue = returnNode.value
        returnValueStr = ast.unparse(returnValue)
        diceResultExpr = self.translateBooleanExpression(returnValueStr)

        self.totalDice += diceResultExpr + " "

    def get_program(self):
        return self.totalDice