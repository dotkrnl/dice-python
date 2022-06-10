import ast


class DiceVisitor(ast.NodeVisitor):

  def __init__(self):
    self.totalDice = [[]]
    self.lastStatementInIf = False
    self.numberOfIfs = 0
    self.allowMoreExpr = True

  def append_dice(self, expr, alwaysAllow, allowMoreExpr):
    if alwaysAllow or self.allowMoreExpr:
      self.totalDice[-1].append(expr)
      self.allowMoreExpr = allowMoreExpr

  def translate_boolean_expr(self, textWhitespace):
    diceBooleanExp = ""

    # split by whitespace: "or" and "and" Python operators are always
    # separated by whitespace
    text = textWhitespace.split(" ")

    for textSegment in text:
      if "" != textSegment:
        if "or" == textSegment:
          diceBooleanExp += " || "
        elif "and" == textSegment:
          diceBooleanExp += " && "
        elif ("not" == textSegment):
          diceBooleanExp += "!"
        # this happens if you start an expression with an open parentheses
        # and have a "not" right after that.  If there is a space in between,
        # it will be handled in "not" instead.
        elif ("(not" == textSegment):
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

  def is_assign_random_choice(self, assignNode):

    # holds variables that we need to define in Dice
    vars = []

    # for every target (vars that are being assigned), if that target is
    # a Name, and that Name also is a Store (we don't want a Load), then
    # we want to record that target so we can use it in our transformation
    # to Dice code
    for target in assignNode.targets:
      if isinstance(target, ast.Name):
        if isinstance(target.ctx, ast.Store):
          vars.append(target.id)

    # for the one value node, record that value so we can use it in our
    # transformation to Dice code
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
      if (isinstance(funcNode, ast.Attribute) and
              "choices" == funcNode.attr):
        if isinstance(funcNode.value, ast.Name):
          nameNode = funcNode.value
          if ("random" == nameNode.id and
                  isinstance(nameNode.ctx, ast.Load)):
            isRandomChoices = True

      isTrueOrFalseConstants = False
      if isRandomChoices:
        # check if arguments are True or False constants
        for args in argsNode:
          if (isinstance(args, ast.List) and
                  isinstance(args.ctx, ast.Load)):
            for argument in args.elts:
              if ((isinstance(argument, ast.NameConstant) and
                   True == argument.value or False == argument.value)):
                isTrueOrFalseConstants = True

      if isTrueOrFalseConstants:
        # check if weights are valid
        for keyword in keywordsNode:
          if ((isinstance(keyword.value, ast.List) and
               isinstance(keyword.value.ctx, ast.Load))):
            weight = keyword.value.elts[0].n
            weight /= 10  # to convert to probability

            for var in vars:
              self.append_dice(
                  "let " + var + " = flip " + str(weight) + " in ",
                  False, True)

            # if lastStatementIf is true, need to finish "in" portion
            if self.lastStatementInIf and self.numberOfIfs > 0:
              self.append_dice(len(self.totalDice), False, False)
              self.lastStatementInIf = False

      if isTrueOrFalseConstants:
        return True
      return False

  def is_assign_boolean_operation(self, assignNode):

    vars = []

    for target in assignNode.targets:
      if isinstance(target, ast.Name):
        if isinstance(target.ctx, ast.Store):
          vars.append(target.id)

    valueNode = assignNode.value
    if isinstance(valueNode, ast.BoolOp):
      # no "<var =" part of assignment, just need the boolean expression
      booleanExpr = ast.unparse(assignNode).split(vars[-1] + " = ")[1]
      booleanExprStr = self.translate_boolean_expr(booleanExpr)

      for var in vars:
        self.append_dice(
            "let " + var + " = " + booleanExprStr + " in ", False, True)

      if self.lastStatementInIf:
        self.append_dice(len(self.totalDice), False, False)
        self.lastStatementInIf = False

      return True
    return False

  def is_assign_constant(self, assignNode):

    vars = []

    for target in assignNode.targets:
      if isinstance(target, ast.Name):
        if isinstance(target.ctx, ast.Store):
          vars.append(target.id)

    valueNode = assignNode.value
    if isinstance(valueNode, ast.Constant):
      constantStr = ast.unparse(valueNode)
      diceConstantStr = self.translate_boolean_expr(constantStr)

      for var in vars:
        self.append_dice(
            "let " + var + " = " + diceConstantStr + " in ", False, True)

      if self.lastStatementInIf:
        self.append_dice(len(self.totalDice), False, False)
        self.lastStatementInIf = False

      return True
    return False

  def visit_FunctionDef(self, functionDefNode):
    for bodyNode in functionDefNode.body:
      super().visit(bodyNode)

  def visit_Assign(self, assignNode):

    if self.is_assign_random_choice(assignNode):
      return
    elif self.is_assign_boolean_operation(assignNode):
      return
    elif self.is_assign_constant(assignNode):
      return

  def visit_If(self, ifNode):

    self.numberOfIfs += 1

    ifCondition = ifNode.test
    ifBody = ifNode.body
    restOfIf = ifNode.orelse

    ifConditionStr = ast.unparse(ifCondition)
    self.append_dice("if " + ifConditionStr + " then ", False, True)

    ifBodyListLength = len(ifBody) - 1
    for node in ifBody:
      if ifBody.index(node) == ifBodyListLength:
        self.lastStatementInIf = True
      super().visit(node)

    self.numberOfIfs -= 1
    if (0 == self.numberOfIfs and 0 == len(restOfIf)):
      self.append_dice("else ", True, True)
    else:
      self.append_dice("else ", True, True)
      for node in restOfIf:
        super().visit(node)
      self.totalDice.append([])

  def visit_Return(self, returnNode):

    returnValue = returnNode.value
    returnValueStr = ast.unparse(returnValue)
    diceResultExpr = self.translate_boolean_expr(returnValueStr)

    self.append_dice(diceResultExpr + " ", False, False)

  def get_program_recursive(self, idx):
    totalDiceLayer = [
        item if type(item) is str
        else self.get_program_recursive(item)
        for item in self.totalDice[idx]]
    if idx < len(self.totalDice) - 1:
      totalDiceLayer.append(self.get_program_recursive(idx+1))
    return ''.join(totalDiceLayer)

  def get_program(self):
    return self.get_program_recursive(0)
