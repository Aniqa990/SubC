import ASTNodes as AST


def pretty_print_ast(node, indent=0):
    """
    Recursively pretty-print an AST node with indentation.
    """
    prefix = "  " * indent
    
    if isinstance(node, AST.Program):
        print(f"{prefix}Program")
        for func in node.getFunction():
            pretty_print_ast(func, indent + 1)
    
    elif isinstance(node, AST.Function):
        print(f"{prefix}Function: {node.getName()}")
        print(f"{prefix}  return_type: {node.getReturnType()}")
        if node.getParams():
            print(f"{prefix}  params:")
            for (typ, name) in node.getParams():
                print(f"{prefix}    ({typ}, {name})")
        print(f"{prefix}  body:")
        pretty_print_ast(node.getStatement(), indent + 2)
    
    elif isinstance(node, AST.Block):
        print(f"{prefix}Block")
        for stmt in node.statements:
            pretty_print_ast(stmt, indent + 1)
    
    elif isinstance(node, AST.VarDecl):
        init_str = f" = {node.init}" if node.init else ""
        print(f"{prefix}VarDecl: {node.typ} {node.name}{init_str}")
        if node.init:
            pretty_print_ast(node.init, indent + 1)
    
    elif isinstance(node, AST.Assign):
        print(f"{prefix}Assign")
        print(f"{prefix}  target:")
        pretty_print_ast(node.target, indent + 2)
        print(f"{prefix}  value:")
        pretty_print_ast(node.expr, indent + 2)
    
    elif isinstance(node, AST.Return):
        print(f"{prefix}Return")
        pretty_print_ast(node.getExpression(), indent + 1)
    
    elif isinstance(node, AST.IfElse):
        print(f"{prefix}IfElse")
        print(f"{prefix}  condition:")
        pretty_print_ast(node.cond, indent + 2)
        print(f"{prefix}  then:")
        pretty_print_ast(node.then_branch, indent + 2)
        if node.else_branch:
            print(f"{prefix}  else:")
            pretty_print_ast(node.else_branch, indent + 2)
    
    elif isinstance(node, AST.While):
        print(f"{prefix}While")
        print(f"{prefix}  condition:")
        pretty_print_ast(node.cond, indent + 2)
        print(f"{prefix}  body:")
        pretty_print_ast(node.body, indent + 2)
    
    elif isinstance(node, AST.For):
        print(f"{prefix}For")
        if node.init:
            print(f"{prefix}  init:")
            pretty_print_ast(node.init, indent + 2)
        if node.cond:
            print(f"{prefix}  condition:")
            pretty_print_ast(node.cond, indent + 2)
        if node.step:
            print(f"{prefix}  step:")
            pretty_print_ast(node.step, indent + 2)
        print(f"{prefix}  body:")
        pretty_print_ast(node.body, indent + 2)
    
    elif isinstance(node, AST.FuncCall):
        print(f"{prefix}FuncCall: {node.name}")
        if node.args:
            print(f"{prefix}  args:")
            for arg in node.args:
                pretty_print_ast(arg, indent + 2)
    
    elif isinstance(node, AST.Print):
        print(f"{prefix}Print")
        pretty_print_ast(node.expr, indent + 1)
    
    elif isinstance(node, AST.Read):
        print(f"{prefix}Read")
        pretty_print_ast(node.target, indent + 1)
    
    elif isinstance(node, AST.BinOp):
        print(f"{prefix}BinOp: {node.oper}")
        print(f"{prefix}  left:")
        pretty_print_ast(node.left, indent + 2)
        print(f"{prefix}  right:")
        pretty_print_ast(node.right, indent + 2)
    
    elif isinstance(node, AST.UnOp):
        print(f"{prefix}UnOp: {node.getOperator()}")
        pretty_print_ast(node.getExpression(), indent + 1)
    
    elif isinstance(node, AST.Constant):
        print(f"{prefix}Constant: {node.getValue()}")
    
    elif isinstance(node, AST.Identifier):
        print(f"{prefix}Identifier: {node.name}")
    
    else:
        print(f"{prefix}{type(node).__name__}: {node}")
