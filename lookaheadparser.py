import sys
import ASTNodes as AST

token_list = []


def parse(tokens):
    global token_list
    token_list = list(tokens)
    return Program()


# --- Grammar nonterminals (recursive-descent) ---


def Program():
    # Program → FunctionList
    funcs = FunctionList()
    return AST.Program(funcs)


def FunctionList():
    # FunctionList → Function FunctionList | Function
    funcs = []
    while lookahead() is not None:
        # Expect top-level function declarations to start with 'func'
        la = lookahead()
        if la[0] == 'Keyword' and la[1] == 'func':
            funcs.append(Function())
        else:
            # Anything else at top-level is a parse error
            fail('Expected top-level function starting with "func"')
    return funcs


def Function():
    # Function → 'func' Type Identifier '(' ParamListOpt ')' Block
    t = nextToken()
    if t[0] != 'Keyword' or t[1] != 'func':
        fail('Expected func at start of function')
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected function name identifier')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after function name')
    params = ParamListOpt()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after parameter list')
    body = Block()
    return AST.Function(idtok[1], body)


def ParamListOpt():
    # ParamListOpt → ParamList | ε
    la = lookahead()
    if la is None or la[0] == 'Close-Paren':
        return []
    return ParamList()


def ParamList():
    # ParamList → Param (',' Param)*
    params = []
    params.append(Param())
    while lookahead() and lookahead()[0] == 'Comma':
        nextToken()
        params.append(Param())
    return params


def Param():
    # Param → Type Identifier
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected parameter name')
    return (typ, idtok[1])


def Type():
    la = lookahead()
    if la is None or la[0] != 'Type':
        fail('Expected type')
    return nextToken()[1]


def Block():
    t = nextToken()
    if t[0] != 'Open-Brace':
        fail('Expected { to start block')
    stmts = StmtList()
    t = nextToken()
    if t[0] != 'Close-Brace':
        fail('Expected } to close block')
    return AST.Block(stmts)


def StmtList():
    # StmtList → Stmt StmtList | ε
    stmts = []
    while lookahead() is not None and lookahead()[0] != 'Close-Brace':
        stmts.append(Stmt())
    return stmts


def Stmt():
    # Stmt -> try all productions based on lookahead
    la = lookahead()
    if la is None:
        fail('Unexpected EOF in statement')

    # Variable declaration starts with a type
    if la[0] == 'Type':
        return VarDecl()

    # AssignmentStmt | FuncCallStmt | ExprStmt begin with Identifier
    if la[0] == 'Identifier':
        idtok = nextToken()
        la2 = lookahead()

        # AssignmentStmt: Identifier '=' Expr ';'
        if la2 and la2[0] == 'Assign':
            nextToken()
            expr = Expr()
            t = nextToken()
            if t[0] != 'Semicolon':
                fail('Missing ; after assignment')
            return AST.Assign(AST.Identifier(idtok[1]), expr)

        # FuncCallStmt: Identifier '(' ArgListOpt ')' ';'
        if la2 and la2[0] == 'Open-Paren':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'Close-Paren':
                fail('Missing ) after function call')
            t = nextToken()
            if t[0] != 'Semicolon':
                fail('Missing ; after function call')
            return AST.FuncCall(idtok[1], args)

        # ExprStmt (identifier-only expression)
        t = nextToken()
        if t[0] != 'Semicolon':
            fail('Missing ; after expression')
        return AST.Identifier(idtok[1])

    # Keywords -> delegate to the matching statement parser
    if la[0] == 'Keyword':
        if la[1] == 'if':
            return IfStmt()
        if la[1] == 'while':
            return WhileStmt()
        if la[1] == 'for':
            return ForStmt()
        if la[1] == 'return':
            return ReturnStmt()
        if la[1] == 'print':
            return PrintStmt()
        if la[1] == 'read':
            return ReadStmt()

    # identifier-led statements: assignment, function call, or identifier expression

    if la[0] == 'Identifier':
        idtok = nextToken()
        la2 = lookahead()

        # AssignmentStmt: Identifier '=' Expr ';'
        if la2 and la2[0] == 'Assign':
            nextToken()
            expr = Expr()
            t = nextToken()
            if t[0] != 'Semicolon':
                fail('Missing ; after assignment')
            return AST.Assign(AST.Identifier(idtok[1]), expr)

        # FuncCallStmt: Identifier '(' ArgListOpt ')' ';'
        if la2 and la2[0] == 'Open-Paren':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'Close-Paren':
                fail('Missing ) after function call')
            t = nextToken()
            if t[0] != 'Semicolon':
                fail('Missing ; after function call')
            return AST.FuncCall(idtok[1], args)

        # ExprStmt (identifier-only expression)
        t = nextToken()
        if t[0] != 'Semicolon':
            fail('Missing ; after expression')
        return AST.Identifier(idtok[1])

    # In other cases, try parsing an expression statement
    if la[0] in ('Integer', 'Float', 'Boolean', 'Open-Paren') or (la[0] == 'Operator' and la[1] in ('-', '!')):
        expr = Expr()
        t = nextToken()
        if t[0] != 'Semicolon':
            fail('Missing ; after expression')
        return expr

    fail('Unknown statement start: %r' % (la,))


### Declarations & VarInit


def VarInitOpt():
    if lookahead() and lookahead()[0] == 'Assign':
        nextToken()
        return Expr()
    return None


def VarDecl():
    # VarDecl → Type Identifier VarInitOpt ';'
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected identifier after type')
    init = VarInitOpt()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after variable declaration')
    return AST.VarDecl(typ, idtok[1], init)


def AssignmentStmt():
    # AssignmentStmt -> Identifier '=' Expr ';'
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected identifier at start of assignment')
    t = nextToken()
    if t[0] != 'Assign':
        fail('Expected = in assignment')
    expr = Expr()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after assignment')
    return AST.Assign(AST.Identifier(idtok[1]), expr)


def FuncCallStmt():
    # FuncCallStmt -> Identifier '(' ArgListOpt ')' ';'
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected identifier at start of function call')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after function name')
    args = ArgListOpt()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after function call')
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after function call')
    return AST.FuncCall(idtok[1], args)


def ExprStmt():
    # ExprStmt -> Expr ';'
    expr = Expr()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after expression')
    return expr


def IfStmt():
    # IfStmt → if '(' Expr ')' Block ElseOpt
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'if':
        fail('Expected if')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after if')
    cond = Expr()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after if')
    then_blk = Block()
    else_blk = ElseOpt()
    return AST.IfElse(cond, then_blk, else_blk)


def WhileStmt():
    # WhileStmt -> while '(' Expr ')' Block
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'while':
        fail('Expected while')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after while')
    cond = Expr()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after while')
    body = Block()
    return AST.While(cond, body)


def ForStmt():
    # ForStmt -> for '(' ForInit ';' ForCond ';' ForStep ')' Block
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'for':
        fail('Expected for')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after for')
    init = ForInit()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Expected ; after for init')
    cond = ForCond()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Expected ; after for condition')
    step = ForStep()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Expected ) after for header')
    body = Block()
    return AST.For(init, cond, step, body)


def ReturnStmt():
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'return':
        fail('Expected return')
    expr = Expr()
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after return')
    return AST.Return(expr)


def PrintStmt():
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'print':
        fail('Expected print')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after print')
    expr = Expr()
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after print')
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after print')
    return AST.Print(expr)


def ReadStmt():
    tok = nextToken()
    if tok[0] != 'Keyword' or tok[1] != 'read':
        fail('Expected read')
    t = nextToken()
    if t[0] != 'Open-Paren':
        fail('Expected ( after read')
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected identifier inside read()')
    t = nextToken()
    if t[0] != 'Close-Paren':
        fail('Missing ) after read')
    t = nextToken()
    if t[0] != 'Semicolon':
        fail('Missing ; after read')
    return AST.Read(AST.Identifier(idtok[1]))


### For header helpers


def VarDeclNoSemicolon():
    # VarDeclNoSemicolon → Type Identifier VarInitOpt
    la = lookahead()
    if la is None or la[0] != 'Type':
        return None
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'Identifier':
        fail('Expected identifier in var declaration')
    init = VarInitOpt()
    return AST.VarDecl(typ, idtok[1], init)


def AssignmentExpr():
    # AssignmentExpr → Identifier '=' Expr (no semicolon expected)
    la = lookahead()
    if la is None or la[0] != 'Identifier':
        return None
    idtok = nextToken()
    if lookahead() and lookahead()[0] == 'Assign':
        nextToken()
        return AST.Assign(AST.Identifier(idtok[1]), Expr())
    fail('Invalid assignment expression')


def ForInit():
    # ForInit → VarDeclNoSemicolon | AssignmentExpr | ε
    if lookahead() is None:
        return None
    if lookahead()[0] == 'Type':
        return VarDeclNoSemicolon()
    if lookahead()[0] == 'Identifier' and len(token_list) > 1 and token_list[1][0] == 'Assign':
        return AssignmentExpr()
    return None


def ElseOpt():
    # ElseOpt → else Block | ε
    la = lookahead()
    if la and la[0] == 'Keyword' and la[1] == 'else':
        nextToken()
        return Block()
    return None


def ForCond():
    # ForCond → Expr | ε
    if lookahead() is None or lookahead()[0] == 'Semicolon':
        return None
    return Expr()


def ForStep():
    # ForStep → AssignmentExpr | ε
    if lookahead() is None:
        return None
    if lookahead()[0] == 'Identifier' and len(token_list) > 1 and token_list[1][0] == 'Assign':
        return AssignmentExpr()
    return None


### Expressions (precedence)


def Expr():
    # Expr -> LogicalOr
    return LogicalOr()


def LogicalOr():
    # LogicalOr → LogicalAnd LogicalOrTail
    left = LogicalAnd()
    return LogicalOrTail(left)


def LogicalOrTail(left):
    # LogicalOrTail → '||' LogicalAnd LogicalOrTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] == '||':
        nextToken()
        right = LogicalAnd()
        combined = AST.BinOp(left, '||', right)
        return LogicalOrTail(combined)
    return left


def LogicalAnd():
    # LogicalAnd → Equality EqualityTail
    left = Equality()
    return EqualityTail(left)


def EqualityTail(left):
    # EqualityTail → '&&' Equality EqualityTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] == '&&':
        nextToken()
        right = Equality()
        combined = AST.BinOp(left, '&&', right)
        return EqualityTail(combined)
    return left


def Equality():
    # Equality → Relational EqualityOpTail
    left = Relational()
    return EqualityOpTail(left)


def EqualityOpTail(left):
    # EqualityOpTail → ('=='|'!=') Relational EqualityOpTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] in ('==', '!='):
        op = nextToken()[1]
        right = Relational()
        combined = AST.BinOp(left, op, right)
        return EqualityOpTail(combined)
    return left


def Relational():
    # Relational → Additive RelOpTail
    left = Additive()
    return RelOpTail(left)


def RelOpTail(left):
    # RelOpTail → RelOp Additive RelOpTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] in ('<', '>', '<=', '>='):
        op = nextToken()[1]
        right = Additive()
        combined = AST.BinOp(left, op, right)
        return RelOpTail(combined)
    return left


def Additive():
    # Additive → Multiplicative AddOpTail
    left = Multiplicative()
    return AddOpTail(left)


def AddOpTail(left):
    # AddOpTail → AddOp Multiplicative AddOpTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] in ('+', '-'):
        op = nextToken()[1]
        right = Multiplicative()
        combined = AST.BinOp(left, op, right)
        return AddOpTail(combined)
    return left


def Multiplicative():
    # Multiplicative → Unary MulOpTail
    left = Unary()
    return MulOpTail(left)


def MulOpTail(left):
    # MulOpTail → ('*'|'/'|'%') Unary MulOpTail | ε
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] in ('*', '/', '%'):
        op = nextToken()[1]
        right = Unary()
        combined = AST.BinOp(left, op, right)
        return MulOpTail(combined)
    return left


def Unary():
    # Unary → UnaryOp Unary | Primary
    la = lookahead()
    if la and la[0] == 'Operator' and la[1] in ('-', '!', '~'):
        op = nextToken()[1]
        rhs = Unary()
        return AST.UnOp(op, rhs)
    return Primary()


def Primary():
    # Primary → Integer | Float | Boolean | Identifier | FuncCallExpr | '(' Expr ')'
    la = lookahead()
    if la is None:
        fail('Unexpected EOF in expression')
    tok = nextToken()
    if tok[0] == 'Integer':
        try:
            v = int(tok[1])
        except:
            v = tok[1]
        return AST.Constant(v)
    if tok[0] == 'Float':
        try:
            v = float(tok[1])
        except:
            v = tok[1]
        return AST.Constant(v)
    if tok[0] == 'Boolean':
        return AST.Constant(True if tok[1] == 'true' else False)
    if tok[0] == 'Identifier':
        # FuncCallExpr or identifier
        if lookahead() and lookahead()[0] == 'Open-Paren':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'Close-Paren':
                fail('Missing ) after function call')
            return AST.FuncCall(tok[1], args)
        return AST.Identifier(tok[1])
    if tok[0] == 'Open-Paren':
        expr = Expr()
        t = nextToken()
        if t[0] != 'Close-Paren':
            fail('Missing )')
        return expr
    fail('Unexpected token %r in primary' % (tok,))


def ArgListOpt():
    # ArgListOpt → ArgList | ε
    if lookahead() and lookahead()[0] == 'Close-Paren':
        return []
    return ArgList()


def ArgList():
    # ArgList → Expr (',' Expr)*
    args = []
    args.append(Expr())
    while lookahead() and lookahead()[0] == 'Comma':
        nextToken()
        args.append(Expr())
    return args


def fail(err):
    print('ERROR ' + err)
    sys.exit()


def nextToken():
    global token_list
    if not token_list:
        fail('Unexpected end of input (no more tokens)')
    a = token_list[0]
    token_list = token_list[1:]
    return a


def lookahead():
    global token_list
    if not token_list:
        return None
    return token_list[0]
