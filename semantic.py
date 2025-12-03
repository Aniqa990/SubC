import sys
import ASTNodes as AST


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        # global function table: name -> (return_type, params_list)
        self.functions = {}
        # current scopes stack: list of dict name->type
        self.scopes = []
        self.current_function = None
        # store symbol tables per function: func_name -> list of scope dicts
        # each scope dict: { 'label': str, 'symbols': { name: {type, addr, info} } }
        self.function_symbols = {}
        # temporary list to collect scopes while analyzing a function
        self._current_function_scopes = None
        # global symbol table for functions and globals: name -> info
        self.global_symbols = {}
        # simple address allocator (unique addresses)
        self._next_addr = 0x1000

    def error(self, msg):
        print('Semantic ERROR: ' + msg)
        raise SemanticError(msg)

    def push_scope(self, label='block'):
        """Push a new lexical scope. Optionally provide a `label` for printing (e.g. 'params', 'for-init')."""
        self.scopes.append({})
        # if inside a function, track this scope for symbol-table printing
        if self.current_function is not None:
            if self._current_function_scopes is None:
                self._current_function_scopes = []
            # record an empty scope with label
            self._current_function_scopes.append({'label': label, 'symbols': {}})

    def pop_scope(self):
        self.scopes.pop()
        # on pop we do not remove the recorded scope info; it's kept for printing

    def declare_var(self, name, typ, kind='local', init_value=None):
        """Declare a variable in the current lexical scope.

        kind: 'param'|'local'
        init_value: optional initializer value for additional info
        """
        if not self.scopes:
            self.error('No active scope to declare variable')
        scope = self.scopes[-1]
        if name in scope:
            self.error(f"Duplicate declaration of variable '{name}' in the same scope")
        scope[name] = typ
        # allocate an address for this symbol
        addr = self._alloc_addr()
        additional = {}
        if init_value is None:
            additional['initialized'] = False
        else:
            additional['initialized'] = True
            additional['init_value'] = init_value
        additional['kind'] = kind

        # record in the current function's symbol table if present
        if self.current_function is not None and self._current_function_scopes is not None and len(self._current_function_scopes) > 0:
            self._current_function_scopes[-1]['symbols'][name] = {'type': typ, 'addr': addr, 'additional': additional}
        else:
            # global scope
            self.global_symbols[name] = {'type': typ, 'addr': addr, 'additional': additional}

    def lookup_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def add_function(self, name, return_type, params):
        if name in self.functions:
            self.error(f"Duplicate function declaration '{name}'")
        self.functions[name] = (return_type, params)
        # also add to global symbol table as function symbol
        addr = self._alloc_addr()
        self.global_symbols[name] = {'type': 'function', 'addr': addr, 'additional': {'returns': return_type, 'params': params}}

    def analyze(self, program: AST.Program):
        funcs = program.getFunction()
        # Expect funcs to be a list
        if funcs is None:
            return

        # First pass: collect function signatures
        for f in funcs:
            if not isinstance(f, AST.Function):
                self.error('Top-level non-function declaration')
            self.add_function(f.getName(), f.getReturnType(), f.getParams())

        # Second pass: analyze each function body
        for f in funcs:
            self.analyze_function(f)

        print('Semantic: no errors')

    def analyze_function(self, func: AST.Function):
        self.current_function = func
        # prepare per-function symbol tracking
        self._current_function_scopes = []
        # function entry scope (params + locals)
        self.push_scope(label='function')
        # add parameters to scope (recorded in first scope)
        for (t, name) in func.getParams():
            self.declare_var(name, t, kind='param')

        # analyze body
        self.analyze_block(func.getStatement())

        # save a copy of the scopes recorded for this function
        # deep copy minimal structure
        self.function_symbols[func.getName()] = [ {'label': s['label'], 'symbols': dict(s['symbols'])} for s in self._current_function_scopes ]

        # clean up
        self._current_function_scopes = None
        self.pop_scope()
        self.current_function = None

    def _alloc_addr(self):
        a = self._next_addr
        self._next_addr += 4
        return hex(a)

    def print_symbol_tables(self):
        print('\n--- Symbol Tables ---')
        # Print globals (functions and any globals)
        if self.global_symbols:
            print('\nGlobals:')
            print(f"{'Name':20} {'Type':12} {'Scope':8} {'Level':6} {'Address':12} {'Additional Info'}")
            for name, info in self.global_symbols.items():
                typ = info.get('type')
                addr = info.get('addr')
                additional = info.get('additional', {})
                if typ == 'function':
                    add_str = f"returns={additional.get('returns')}, params={additional.get('params')}"
                else:
                    add_str = ', '.join([f"{k}={v}" for k, v in additional.items()])
                print(f"{name:20} {typ:12} {'Global':8} {'-':6} {addr:12} {add_str}")

        # Print per-function symbol tables (scoped)
        for fname, scopes in self.function_symbols.items():
            print(f"\nFunction: {fname}")
            print(f"{'Name':20} {'Type':12} {'Scope':12} {'Address':12} {'Additional Info'}")
            for i, scope in enumerate(scopes):
                label = scope.get('label', f'scope[{i}]')
                for vname, vinfo in scope.get('symbols', {}).items():
                    typ = vinfo.get('type')
                    addr = vinfo.get('addr')
                    additional = vinfo.get('additional', {})
                    # scope type: parameter vs local
                    kind = additional.get('kind', 'local')
                    add_items = []
                    for k, v in additional.items():
                        add_items.append(f"{k}={v}")
                    add_str = ', '.join(add_items)
                    scope_display = f"{label}({kind})"
                    # print Level as the scope index i
                    print(f"{vname:20} {typ:12} {scope_display:12} {i:<6} {addr:12} {add_str}")
        print('\n--- End Symbol Tables ---\n')

    # (old simple printer removed)

    def analyze_block(self, block: AST.Block):
        # block.statements is a list
        self.push_scope()
        for stmt in block.statements:
            self.analyze_stmt(stmt)
        self.pop_scope()

    def analyze_stmt(self, stmt):
        t = type(stmt)
        if t is AST.VarDecl:
            # VarDecl(type, name, init)
            self.declare_var(stmt.name, stmt.typ)
            if stmt.init is not None:
                expr_type = self.type_of(stmt.init)
                if not self.is_assignable(stmt.typ, expr_type):
                    self.error(f"Cannot initialize variable '{stmt.name}' of type {stmt.typ} with {expr_type}")
        elif t is AST.Assign:
            # Assign(target Identifier, expr)
            if not isinstance(stmt.target, AST.Identifier):
                self.error('Assignment target must be an identifier')
            name = stmt.target.name
            var_type = self.lookup_var(name)
            if var_type is None:
                self.error(f"Use of undeclared variable '{name}'")
            expr_type = self.type_of(stmt.expr)
            if not self.is_assignable(var_type, expr_type):
                self.error(f"Cannot assign {expr_type} to variable '{name}' of type {var_type}")
        elif t is AST.Return:
            expr_type = self.type_of(stmt.getExpression())
            expected = self.current_function.getReturnType()
            if expected is None:
                self.error('Function missing return type')
            if not self.is_assignable(expected, expr_type):
                self.error(f"Return type mismatch in function '{self.current_function.getName()}': expected {expected}, got {expr_type}")
        elif t is AST.IfElse:
            cond_type = self.type_of(stmt.cond)
            if not self.is_boolean_compatible(cond_type):
                self.error('If-condition not boolean-compatible')
            self.analyze_block(stmt.then_branch)
            if stmt.else_branch:
                self.analyze_block(stmt.else_branch)
        elif t is AST.While:
            cond_type = self.type_of(stmt.cond)
            if not self.is_boolean_compatible(cond_type):
                self.error('While-condition not boolean-compatible')
            self.analyze_block(stmt.body)
        elif t is AST.For:
            # The for-loop header should introduce a scope that covers init, cond, step, and the loop body.
            self.push_scope()
            if stmt.init is not None:
                self.analyze_stmt(stmt.init)
            if stmt.cond is not None:
                if not self.is_boolean_compatible(self.type_of(stmt.cond)):
                    self.error('For-condition not boolean-compatible')
            if stmt.step is not None:
                self.analyze_stmt(stmt.step)
            # analyze body statements in the same for-scope
            for s in stmt.body.statements:
                self.analyze_stmt(s)
            self.pop_scope()
        elif t is AST.FuncCall:
            # function call statement: check call validity
            self.check_funccall(stmt)
        elif t is AST.Print:
            _ = self.type_of(stmt.expr)
        elif t is AST.Read:
            if not isinstance(stmt.target, AST.Identifier):
                self.error('read() target must be identifier')
            if self.lookup_var(stmt.target.name) is None:
                self.error(f"Use of undeclared variable '{stmt.target.name}' in read()")
        elif t is AST.Identifier:
            # expression statement with an identifier
            if self.lookup_var(stmt.name) is None:
                self.error(f"Use of undeclared identifier '{stmt.name}'")
        else:
            # unknown/unsupported statement type
            pass

    def check_funccall(self, node: AST.FuncCall):
        name = node.name
        if name not in self.functions:
            self.error(f"Call to undefined function '{name}'")
        ret_type, params = self.functions[name]
        if len(node.args) != len(params):
            self.error(f"Function '{name}' expects {len(params)} args, got {len(node.args)}")
        for i, arg in enumerate(node.args):
            expected_type = params[i][0]
            actual_type = self.type_of(arg)
            if not self.is_assignable(expected_type, actual_type):
                self.error(f"Argument {i+1} of function '{name}' expects {expected_type}, got {actual_type}")

    def type_of(self, expr):
        # Return a type string like 'int', 'float', 'bool'
        if expr is None:
            return None
        if isinstance(expr, AST.Constant):
            v = expr.getValue()
            if isinstance(v, bool):
                return 'bool'
            if isinstance(v, float):
                return 'float'
            if isinstance(v, int):
                return 'int'
            # fallback: try to parse
            s = str(v)
            if s in ('true', 'false'):
                return 'bool'
            if '.' in s:
                return 'float'
            return 'int'
        if isinstance(expr, AST.Identifier):
            typ = self.lookup_var(expr.name)
            if typ is None:
                self.error(f"Use of undeclared variable '{expr.name}'")
            return typ
        if isinstance(expr, AST.UnOp):
            op = expr.getOperator()
            inner = expr.getExpression()
            t = self.type_of(inner)
            if op == '!':
                if not self.is_boolean_compatible(t):
                    self.error('Operator ! requires boolean-compatible operand')
                return 'bool'
            if op == '~':
                if t != 'int':
                    self.error('Operator ~ requires integer operand')
                return 'int'
            if op == '-':
                if t not in ('int', 'float'):
                    self.error('Unary - requires numeric operand')
                return t
        if isinstance(expr, AST.BinOp):
            left_t = self.type_of(expr.left)
            right_t = self.type_of(expr.right)
            op = expr.oper
            if op in ('+', '-', '*', '/', '%'):
                if left_t not in ('int', 'float') or right_t not in ('int', 'float'):
                    self.error(f"Operator {op} requires numeric operands")
                # if either float -> float, else int
                if left_t == 'float' or right_t == 'float' or op == '/':
                    return 'float'
                return 'int'
            if op in ('==', '!=', '<', '>', '<=', '>='):
                # comparisons -> bool
                return 'bool'
            if op in ('&&', '||'):
                return 'bool'
        if isinstance(expr, AST.FuncCall):
            name = expr.name
            if name not in self.functions:
                self.error(f"Call to undefined function '{name}'")
            ret_type, params = self.functions[name]
            # also validate args here
            if len(expr.args) != len(params):
                self.error(f"Function '{name}' expects {len(params)} args, got {len(expr.args)}")
            for i, arg in enumerate(expr.args):
                expected_type = params[i][0]
                actual_type = self.type_of(arg)
                if not self.is_assignable(expected_type, actual_type):
                    self.error(f"Argument {i+1} of function '{name}' expects {expected_type}, got {actual_type}")
            return ret_type

        # Unknown expression type: be permissive
        return None

    def is_assignable(self, target_type, expr_type):
        # allow exact match; allow int -> float promotion
        if target_type == expr_type:
            return True
        if target_type == 'float' and expr_type == 'int':
            return True
        return False

    def is_boolean_compatible(self, typ):
        return typ == 'bool' or typ in ('int', 'float')
