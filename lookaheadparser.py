import sys
import ASTNodes as AST
import lexer

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
        if la[0] == 'func':
            funcs.append(Function())
        else:
            # Anything else at top-level is a parse error
            fail('Expected top-level function starting with "func"')
    return funcs


def Function():
    # Function → 'func' Type Identifier '(' ParamListOpt ')' Block
    t = nextToken()
    if t[0] != 'func':
        fail('Expected func at start of function')
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected function name identifier')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after function name')
    params = ParamListOpt()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after parameter list')
    body = Block()
    # Pass return type and parameters into AST.Function
    # Note: idtok = ('identifier', name, lineNumber, symbol_ref); we ignore symbol_ref for functions
    return AST.Function(idtok[1], typ, params, body)


def ParamListOpt():
    # ParamListOpt → ParamList | ε
    la = lookahead()
    if la is None or la[0] == 'rparen':
        return []
    return ParamList()


def ParamList():
    # ParamList → Param (',' Param)*
    params = []
    params.append(Param())
    while lookahead() and lookahead()[0] == 'comma':
        nextToken()
        params.append(Param())
    return params


def Param():
    # Param → Type Identifier
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected parameter name')
    return (typ, idtok[1])


def Type():
    la = lookahead()
    if la is None or la[0] not in lexer.types:
        fail('Expected type')
    return nextToken()[1]


def Block():
    t = nextToken()
    if t[0] != 'lbrace':
        fail('Expected { to start block')
    stmts = StmtList()
    t = nextToken()
    if t[0] != 'rbrace':
        fail('Expected } to close block')
    return AST.Block(stmts)


def StmtList():
    # StmtList → Stmt StmtList | ε
    stmts = []
    while lookahead() is not None and lookahead()[0] != 'rbrace':
        stmts.append(Stmt())
    return stmts


def Stmt():
    # Stmt -> try all productions based on lookahead
    la = lookahead()
    if la is None:
        fail('Unexpected EOF in statement')

    # Variable declaration starts with a type
    if la[0] in lexer.types:
        return VarDecl()

    # AssignmentStmt | FuncCallStmt | ExprStmt begin with Identifier
    if la[0] == 'identifier':
        idtok = nextToken()
        la2 = lookahead()
        # idtok[3] is symbol_ref from token
        symbol_ref = idtok[3] if len(idtok) > 3 else None

        # AssignmentStmt: Identifier '=' Expr ';'
        if la2 and la2[0] == 'assign':
            nextToken()
            expr = Expr()
            t = nextToken()
            if t[0] != 'semicolon':
                fail('Missing ; after assignment')
            return AST.Assign(AST.Identifier(idtok[1], symbol_ref), expr)

        # FuncCallStmt: Identifier '(' ArgListOpt ')' ';'
        if la2 and la2[0] == 'lparen':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'rparen':
                fail('Missing ) after function call')
            t = nextToken()
            if t[0] != 'semicolon':
                fail('Missing ; after function call')
            return AST.FuncCall(idtok[1], args, symbol_ref)

        # ExprStmt (identifier-only expression)
        t = nextToken()
        if t[0] != 'semicolon':
            fail('Missing ; after expression')
        return AST.Identifier(idtok[1], symbol_ref)

    # Keywords -> delegate to the matching statement parser (keywords are token types now)
    if la[0] == 'if':
        return IfStmt()
    if la[0] == 'while':
        return WhileStmt()
    if la[0] == 'for':
        return ForStmt()
    if la[0] == 'return':
        return ReturnStmt()
    if la[0] == 'print':
        return PrintStmt()
    if la[0] == 'read':
        return ReadStmt()

    # identifier-led statements: assignment, function call, or identifier expression

    if la[0] == 'identifier':
        idtok = nextToken()
        la2 = lookahead()
        # idtok[3] is symbol_ref from token
        symbol_ref = idtok[3] if len(idtok) > 3 else None

        # AssignmentStmt: Identifier '=' Expr ';'
        if la2 and la2[0] == 'assign':
            nextToken()
            expr = Expr()
            t = nextToken()
            if t[0] != 'semicolon':
                fail('Missing ; after assignment')
            return AST.Assign(AST.Identifier(idtok[1], symbol_ref), expr)

        # FuncCallStmt: Identifier '(' ArgListOpt ')' ';'
        if la2 and la2[0] == 'lparen':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'rparen':
                fail('Missing ) after function call')
            t = nextToken()
            if t[0] != 'semicolon':
                fail('Missing ; after function call')
            return AST.FuncCall(idtok[1], args, symbol_ref)

        # ExprStmt (identifier-only expression)
        t = nextToken()
        if t[0] != 'semicolon':
            fail('Missing ; after expression')
        return AST.Identifier(idtok[1], symbol_ref)

    # In other cases, try parsing an expression statement
    if la[0] in ('number', 'lparen') or (la[0] in ('unop', 'addop') and la[1] in ('-', '!')) or la[0] in ('true', 'false'):
        expr = Expr()
        t = nextToken()
        if t[0] != 'semicolon':
            fail('Missing ; after expression')
        return expr

    fail('Unknown statement start: %r' % (la,))


### Declarations & VarInit


def VarInitOpt():
    if lookahead() and lookahead()[0] == 'assign':
        nextToken()
        return Expr()
    return None


def VarDecl():
    # VarDecl → Type Identifier VarInitOpt ';'
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected identifier after type')
    init = VarInitOpt()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after variable declaration')
    # Note: VarDecl stores idtok[1] (name) but ignores symbol_ref; semantic analyzer sets it
    return AST.VarDecl(typ, idtok[1], init)


def AssignmentStmt():
    # AssignmentStmt -> Identifier '=' Expr ';'
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected identifier at start of assignment')
    t = nextToken()
    if t[0] != 'assign':
        fail('Expected = in assignment')
    expr = Expr()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after assignment')
    return AST.Assign(AST.Identifier(idtok[1]), expr)


def FuncCallStmt():
    # FuncCallStmt -> Identifier '(' ArgListOpt ')' ';'
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected identifier at start of function call')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after function name')
    args = ArgListOpt()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after function call')
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after function call')
    return AST.FuncCall(idtok[1], args)


def ExprStmt():
    # ExprStmt -> Expr ';'
    expr = Expr()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after expression')
    return expr


def IfStmt():
    # IfStmt → if '(' Expr ')' Block ElseOpt
    tok = nextToken()
    if tok[0] != 'if':
        fail('Expected if')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after if')
    cond = Expr()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after if')
    then_blk = Block()
    else_blk = ElseOpt()
    return AST.IfElse(cond, then_blk, else_blk)


def WhileStmt():
    # WhileStmt -> while '(' Expr ')' Block
    tok = nextToken()
    if tok[0] != 'while':
        fail('Expected while')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after while')
    cond = Expr()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after while')
    body = Block()
    return AST.While(cond, body)


def ForStmt():
    # ForStmt -> for '(' ForInit ';' ForCond ';' ForStep ')' Block
    tok = nextToken()
    if tok[0] != 'for':
        fail('Expected for')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after for')
    init = ForInit()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Expected ; after for init')
    cond = ForCond()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Expected ; after for condition')
    step = ForStep()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Expected ) after for header')
    body = Block()
    return AST.For(init, cond, step, body)


def ReturnStmt():
    tok = nextToken()
    if tok[0] != 'return':
        fail('Expected return')
    expr = Expr()
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after return')
    return AST.Return(expr)


def PrintStmt():
    tok = nextToken()
    if tok[0] != 'print':
        fail('Expected print')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after print')
    expr = Expr()
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after print')
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after print')
    return AST.Print(expr)


def ReadStmt():
    tok = nextToken()
    if tok[0] != 'read':
        fail('Expected read')
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after read')
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected identifier inside read()')
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after read')
    t = nextToken()
    if t[0] != 'semicolon':
        fail('Missing ; after read')
    # idtok[3] is symbol_ref from token
    return AST.Read(AST.Identifier(idtok[1], idtok[3] if len(idtok) > 3 else None))


### For header helpers


def VarDeclNoSemicolon():
    # VarDeclNoSemicolon → Type Identifier VarInitOpt
    la = lookahead()
    if la is None or la[0] not in lexer.types:
        return None
    typ = Type()
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected identifier in var declaration')
    init = VarInitOpt()
    # Note: VarDecl stores idtok[1] (name) but ignores symbol_ref
    return AST.VarDecl(typ, idtok[1], init)


def AssignmentExpr():
    # AssignmentExpr → Identifier '=' Expr (no semicolon expected)
    la = lookahead()
    if la is None or la[0] != 'identifier':
        return None
    idtok = nextToken()
    if lookahead() and lookahead()[0] == 'assign':
        nextToken()
        # idtok[3] is symbol_ref from token
        return AST.Assign(AST.Identifier(idtok[1], idtok[3] if len(idtok) > 3 else None), Expr())
    fail('Invalid assignment expression')


def ForInit():
    # ForInit → VarDeclNoSemicolon | AssignmentExpr | ε
    if lookahead() is None:
        return None
    if lookahead()[0] in lexer.types:
        return VarDeclNoSemicolon()
    if lookahead()[0] == 'identifier' and len(token_list) > 1 and token_list[1][0] == 'assign':
        return AssignmentExpr()
    return None


def ElseOpt():
    # ElseOpt → else Block | ε
    la = lookahead()
    if la and la[0] == 'else':
        nextToken()
        return Block()
    return None


def ForCond():
    # ForCond → Expr | ε
    if lookahead() is None or lookahead()[0] == 'semicolon':
        return None
    return Expr()


def ForStep():
    # ForStep → AssignmentExpr | ε
    if lookahead() is None:
        return None
    if lookahead()[0] == 'identifier' and len(token_list) > 1 and token_list[1][0] == 'assign':
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
    if la and la[0] == 'logop' and la[1] == '||':
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
    if la and la[0] == 'logop' and la[1] == '&&':
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
    if la and la[0] == 'relop' and la[1] in ('==', '!='):
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
    if la and la[0] == 'relop' and la[1] in ('<', '>', '<=', '>='):
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
    if la and la[0] == 'addop' and la[1] in ('+', '-'):
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
    if la and la[0] in ('mulop', 'divop', 'modop') and la[1] in ('*', '/', '%'):
        op = nextToken()[1]
        right = Unary()
        combined = AST.BinOp(left, op, right)
        return MulOpTail(combined)
    return left


def Unary():
    # Unary → UnaryOp Unary | Primary
    la = lookahead()
    if la and la[0] in ('unop', 'addop') and la[1] in ('-', '!', '~'):
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
    # numbers -> ('number', value)
    if tok[0] == 'number':
        return AST.Constant(tok[1])

    # booleans are now keyword tokens 'true'/'false'
    if tok[0] == 'true' or tok[0] == 'false':
        return AST.Constant(True if tok[0] == 'true' else False)

    # identifier -> possible function call
    if tok[0] == 'identifier':
        # tok[3] is symbol_ref from token
        symbol_ref = tok[3] if len(tok) > 3 else None
        if lookahead() and lookahead()[0] == 'lparen':
            nextToken()
            args = ArgListOpt()
            t = nextToken()
            if t[0] != 'rparen':
                fail('Missing ) after function call')
            return AST.FuncCall(tok[1], args, symbol_ref)
        return AST.Identifier(tok[1], symbol_ref)

    if tok[0] == 'lparen':
        expr = Expr()
        t = nextToken()
        if t[0] != 'rparen':
            fail('Missing )')
        return expr
    fail('Unexpected token %r in primary' % (tok,))


def ArgListOpt():
    # ArgListOpt → ArgList | ε
    if lookahead() and lookahead()[0] == 'rparen':
        return []
    return ArgList()


def ArgList():
    # ArgList → Expr (',' Expr)*
    args = []
    args.append(Expr())
    while lookahead() and lookahead()[0] == 'comma':
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
