import ASTNodes as AST


def pretty_print_ast_tree(node, prefix="", is_last=True):
    r"""
    Pretty-print an AST node as a tree with ASCII characters.
    Uses \-- and |-- for branches, and | for continuations.
    """
    # Determine the connector (using ASCII-safe characters)
    connector = "\\-- " if is_last else "|-- "
    
    # Print the current node
    if isinstance(node, AST.Program):
        print(f"{prefix}{connector}Program")
        _print_children(node.getFunction(), prefix, is_last, lambda x: x)
    
    elif isinstance(node, AST.Function):
        print(f"{prefix}{connector}Function: {node.getName()}")
        new_prefix = _get_new_prefix(prefix, is_last)
        children = [
            ("return_type", node.getReturnType()),
            ("params", node.getParams()),
            ("body", node.getStatement())
        ]
        for i, (label, child) in enumerate(children):
            is_last_child = (i == len(children) - 1)
            child_connector = "\\-- " if is_last_child else "|-- "
            if label == "return_type":
                print(f"{new_prefix}{child_connector}{label}: {child}")
            elif label == "params":
                if child:
                    print(f"{new_prefix}{child_connector}{label}:")
                    child_prefix = _get_new_prefix(new_prefix, is_last_child)
                    for j, (typ, name) in enumerate(child):
                        param_is_last = (j == len(child) - 1)
                        param_connector = "\\-- " if param_is_last else "|-- "
                        print(f"{child_prefix}{param_connector}({typ}, {name})")
            else:
                child_prefix = _get_new_prefix(new_prefix, is_last_child)
                _print_tree_node(child, child_prefix, is_last_child)
    
    elif isinstance(node, AST.Block):
        print(f"{prefix}{connector}Block")
        _print_children(node.statements, prefix, is_last, lambda x: x)
    
    elif isinstance(node, AST.VarDecl):
        print(f"{prefix}{connector}VarDecl: {node.typ} {node.name}")
        if node.init:
            new_prefix = _get_new_prefix(prefix, is_last)
            _print_tree_node(node.init, new_prefix, True)
    
    elif isinstance(node, AST.Assign):
        print(f"{prefix}{connector}Assign")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.target, new_prefix, False)
        _print_tree_node(node.expr, new_prefix, True)
    
    elif isinstance(node, AST.Return):
        print(f"{prefix}{connector}Return")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.getExpression(), new_prefix, True)
    
    elif isinstance(node, AST.IfElse):
        print(f"{prefix}{connector}IfElse")
        new_prefix = _get_new_prefix(prefix, is_last)
        has_else = node.else_branch is not None
        _print_tree_node(node.cond, new_prefix, False)
        _print_tree_node(node.then_branch, new_prefix, not has_else)
        if has_else:
            _print_tree_node(node.else_branch, new_prefix, True)
    
    elif isinstance(node, AST.While):
        print(f"{prefix}{connector}While")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.cond, new_prefix, False)
        _print_tree_node(node.body, new_prefix, True)
    
    elif isinstance(node, AST.For):
        print(f"{prefix}{connector}For")
        new_prefix = _get_new_prefix(prefix, is_last)
        children = []
        if node.init:
            children.append(("init", node.init))
        if node.cond:
            children.append(("condition", node.cond))
        if node.step:
            children.append(("step", node.step))
        children.append(("body", node.body))
        
        for i, (label, child) in enumerate(children):
            child_is_last = (i == len(children) - 1)
            child_connector = "\\-- " if child_is_last else "|-- "
            if label in ("init", "condition", "step"):
                print(f"{new_prefix}{child_connector}{label}:")
                child_prefix = _get_new_prefix(new_prefix, child_is_last)
                _print_tree_node(child, child_prefix, True)
            else:
                _print_tree_node(child, new_prefix, child_is_last)
    
    elif isinstance(node, AST.FuncCall):
        print(f"{prefix}{connector}FuncCall: {node.name}")
        if node.args:
            new_prefix = _get_new_prefix(prefix, is_last)
            _print_children(node.args, prefix, is_last, lambda x: x)
    
    elif isinstance(node, AST.Print):
        print(f"{prefix}{connector}Print")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.expr, new_prefix, True)
    
    elif isinstance(node, AST.Read):
        print(f"{prefix}{connector}Read")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.target, new_prefix, True)
    
    elif isinstance(node, AST.BinOp):
        print(f"{prefix}{connector}BinOp: {node.oper}")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.left, new_prefix, False)
        _print_tree_node(node.right, new_prefix, True)
    
    elif isinstance(node, AST.UnOp):
        print(f"{prefix}{connector}UnOp: {node.getOperator()}")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.getExpression(), new_prefix, True)
    
    elif isinstance(node, AST.Constant):
        print(f"{prefix}{connector}Constant: {node.getValue()}")
    
    elif isinstance(node, AST.Identifier):
        print(f"{prefix}{connector}Identifier: {node.name}")
    
    else:
        print(f"{prefix}{connector}{type(node).__name__}: {node}")


def _print_tree_node(node, prefix, is_last):
    """Helper to print a single tree node with proper prefix."""
    if node is None:
        return
    connector = "\\-- " if is_last else "|-- "
    
    if isinstance(node, AST.Program):
        print(f"{prefix}{connector}Program")
        _print_children(node.getFunction(), prefix, is_last, lambda x: x)
    elif isinstance(node, AST.Function):
        print(f"{prefix}{connector}Function: {node.getName()}")
        new_prefix = _get_new_prefix(prefix, is_last)
        children = [
            ("return_type", node.getReturnType()),
            ("params", node.getParams()),
            ("body", node.getStatement())
        ]
        for i, (label, child) in enumerate(children):
            child_is_last = (i == len(children) - 1)
            child_connector = "\\-- " if child_is_last else "|-- "
            if label == "return_type":
                print(f"{new_prefix}{child_connector}{label}: {child}")
            elif label == "params":
                if child:
                    print(f"{new_prefix}{child_connector}{label}:")
                    param_prefix = _get_new_prefix(new_prefix, child_is_last)
                    for j, (typ, name) in enumerate(child):
                        param_is_last = (j == len(child) - 1)
                        param_connector = "\\-- " if param_is_last else "|-- "
                        print(f"{param_prefix}{param_connector}({typ}, {name})")
            else:
                child_prefix = _get_new_prefix(new_prefix, child_is_last)
                _print_tree_node(child, child_prefix, child_is_last)
    elif isinstance(node, AST.Block):
        print(f"{prefix}{connector}Block")
        new_prefix = _get_new_prefix(prefix, is_last)
        for i, stmt in enumerate(node.statements):
            stmt_is_last = (i == len(node.statements) - 1)
            _print_tree_node(stmt, new_prefix, stmt_is_last)
    elif isinstance(node, AST.VarDecl):
        print(f"{prefix}{connector}VarDecl: {node.typ} {node.name}")
        if node.init:
            new_prefix = _get_new_prefix(prefix, is_last)
            _print_tree_node(node.init, new_prefix, True)
    elif isinstance(node, AST.Assign):
        print(f"{prefix}{connector}Assign")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.target, new_prefix, False)
        _print_tree_node(node.expr, new_prefix, True)
    elif isinstance(node, AST.Return):
        print(f"{prefix}{connector}Return")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.getExpression(), new_prefix, True)
    elif isinstance(node, AST.IfElse):
        print(f"{prefix}{connector}IfElse")
        new_prefix = _get_new_prefix(prefix, is_last)
        has_else = node.else_branch is not None
        _print_tree_node(node.cond, new_prefix, False)
        _print_tree_node(node.then_branch, new_prefix, not has_else)
        if has_else:
            _print_tree_node(node.else_branch, new_prefix, True)
    elif isinstance(node, AST.While):
        print(f"{prefix}{connector}While")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.cond, new_prefix, False)
        _print_tree_node(node.body, new_prefix, True)
    elif isinstance(node, AST.For):
        print(f"{prefix}{connector}For")
        new_prefix = _get_new_prefix(prefix, is_last)
        children = []
        if node.init:
            children.append(("init", node.init))
        if node.cond:
            children.append(("condition", node.cond))
        if node.step:
            children.append(("step", node.step))
        children.append(("body", node.body))
        
        for i, (label, child) in enumerate(children):
            child_is_last = (i == len(children) - 1)
            child_connector = "\\-- " if child_is_last else "|-- "
            if label in ("init", "condition", "step"):
                print(f"{new_prefix}{child_connector}{label}:")
                child_prefix = _get_new_prefix(new_prefix, child_is_last)
                _print_tree_node(child, child_prefix, True)
            else:
                _print_tree_node(child, new_prefix, child_is_last)
    elif isinstance(node, AST.FuncCall):
        print(f"{prefix}{connector}FuncCall: {node.name}")
        if node.args:
            new_prefix = _get_new_prefix(prefix, is_last)
            for i, arg in enumerate(node.args):
                arg_is_last = (i == len(node.args) - 1)
                _print_tree_node(arg, new_prefix, arg_is_last)
    elif isinstance(node, AST.Print):
        print(f"{prefix}{connector}Print")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.expr, new_prefix, True)
    elif isinstance(node, AST.Read):
        print(f"{prefix}{connector}Read")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.target, new_prefix, True)
    elif isinstance(node, AST.BinOp):
        print(f"{prefix}{connector}BinOp: {node.oper}")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.left, new_prefix, False)
        _print_tree_node(node.right, new_prefix, True)
    elif isinstance(node, AST.UnOp):
        print(f"{prefix}{connector}UnOp: {node.getOperator()}")
        new_prefix = _get_new_prefix(prefix, is_last)
        _print_tree_node(node.getExpression(), new_prefix, True)
    elif isinstance(node, AST.Constant):
        print(f"{prefix}{connector}Constant: {node.getValue()}")
    elif isinstance(node, AST.Identifier):
        print(f"{prefix}{connector}Identifier: {node.name}")
    else:
        print(f"{prefix}{connector}{type(node).__name__}: {node}")


def _get_new_prefix(prefix, is_last):
    """Return the prefix for the next level of indentation."""
    return prefix + ("    " if is_last else "|   ")


def _print_children(children, prefix, is_last, extractor):
    """Helper to print a list of children."""
    if not children:
        return
    new_prefix = _get_new_prefix(prefix, is_last)
    for i, child in enumerate(children):
        child_is_last = (i == len(children) - 1)
        _print_tree_node(child, new_prefix, child_is_last)
