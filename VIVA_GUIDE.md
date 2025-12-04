# SubC Compiler - Complete Technical Explanation

## Project Overview

This is a **recursive-descent compiler** for a simplified C-like language (SubC). It processes source code through three main stages:

1. **Lexical Analysis (Tokenization)** - `lexer.py`
2. **Syntax Analysis (Parsing)** - `lookaheadparser.py`
3. **Semantic Analysis** - `semantic.py`

---

## Stage 1: Lexical Analysis (`lexer.py`)

### Purpose
Convert source code (raw text) into a stream of **tokens** (meaningful units).

### How It Works

```python
keywords = ["auto", "struct", "break", ..., "func", "if", "while", "for", ...]
types = ["double", "int", "long", "char", "float", "short", "bool"]
```

The lexer maintains lists of recognized keywords and types.

### Main Function: `lex(source)`

```python
def lex(source):
    token_list = []
    x = 0  # position in source
    newStr = ""  # accumulate identifier/number characters
    
    while x < len(source):
        c = source[x]
        
        # Collect alphanumeric characters, dots, underscores
        if c.isalpha() or c.isdigit() or c == '_' or c == '.':
            newStr += c
            x += 1
            continue
```

**Key Steps:**

1. **Character Accumulation**: Build up identifiers and numbers
2. **Whitespace Handling**: When whitespace is encountered, finalize the current token
3. **Operator/Punctuation Handling**: Recognize special characters

### Token Classification: `check(newStr)`

This function determines what type of token has been accumulated:

```python
def check(newStr):
    # Keywords: emit token type = the keyword itself
    if newStr in keywords:
        return (newStr, newStr, lineNumber)  # e.g., ('if', 'if', 5)
    
    # Types: emit token type = the type name
    if newStr in types:
        return (newStr, newStr, lineNumber)  # e.g., ('int', 'int', 1)
    
    # Numbers: emit ('number', numeric_value, lineNumber)
    if newStr.replace('.', '', 1).isdigit() and newStr.count('.') <= 1:
        if '.' in newStr:
            return ("number", float(newStr), lineNumber)  # ('number', 3.14, 2)
        return ("number", int(newStr), lineNumber)  # ('number', 42, 2)
    
    # Identifiers: emit ('identifier', name, lineNumber, symbol_ref)
    # symbol_ref is a mutable dict that semantic analyzer will populate
    if len(newStr) > 0 and len(newStr) < 32:
        symbol_ref = {}  # Empty dict; filled later
        return ("identifier", newStr, lineNumber, symbol_ref)
```

### Token Shapes (4-tuples)

After lexical analysis, tokens have these formats:

| Token Type | Format | Example |
|-----------|--------|---------|
| Keyword | `(keyword, keyword, line)` | `('if', 'if', 5)` |
| Type | `(typename, typename, line)` | `('int', 'int', 1)` |
| Identifier | `('identifier', name, line, symbol_ref)` | `('identifier', 'x', 2, {})` |
| Number | `('number', value, line)` | `('number', 42, 3)` |
| Operator | `(category, symbol, line)` | `('addop', '+', 4)` |
| Punctuation | `(punct_name, symbol, line)` | `('lparen', '(', 5)` |

### Example: Lexing Code

**Input:**
```c
func int main() {
    int x = 5;
    return 0;
}
```

**Token Output:**
```
('func', 'func', 1)
('int', 'int', 1)
('identifier', 'main', 1, {})
('lparen', '(', 1)
('rparen', ')', 1)
('lbrace', '{', 2)
('int', 'int', 3)
('identifier', 'x', 3, {})
('assign', '=', 3)
('number', 5, 3)
('semicolon', ';', 3)
('return', 'return', 4)
('number', 0, 4)
('semicolon', ';', 4)
('rbrace', '}', 5)
```

---

## Stage 2: Syntax Analysis (`lookaheadparser.py`)

### Purpose
Convert the token stream into an **Abstract Syntax Tree (AST)** that represents the grammatical structure.

### Grammar Rules

The parser implements a **context-free grammar** using recursive-descent parsing:

```
Program         → FunctionList
FunctionList    → Function FunctionList | Function
Function        → 'func' Type Identifier '(' ParamListOpt ')' Block
Block           → '{' StmtList '}'
StmtList        → Stmt StmtList | ε
Stmt            → VarDecl | Assignment | IfStmt | WhileStmt | ForStmt | ReturnStmt | ...
Expr            → LogicalOr
LogicalOr       → LogicalAnd ('||' LogicalAnd)*
LogicalAnd      → Equality ('&&' Equality)*
Equality        → Relational (('=='|'!=') Relational)*
Relational      → Additive (('<'|'>'|'<='|'>=') Additive)*
Additive        → Multiplicative (('+'|'-') Multiplicative)*
Multiplicative  → Unary (('*'|'/'|'%') Unary)*
Unary           → ('-'|'!'|'~') Unary | Primary
Primary         → number | identifier | 'true' | 'false' | '(' Expr ')'
```

This grammar encodes **operator precedence**:
- **Lowest** precedence: Logical OR (`||`)
- **Medium** precedence: Addition/Subtraction (`+`, `-`)
- **Highest** precedence: Unary operators (`-`, `!`, `~`)

### Parser Operation

The parser uses **two helper functions**:

```python
def lookahead():
    """Peek at the next token WITHOUT consuming it"""
    if not token_list:
        return None
    return token_list[0]

def nextToken():
    """Consume and return the next token"""
    if not token_list:
        fail('Unexpected end of input')
    a = token_list[0]
    token_list = token_list[1:]  # Remove from front
    return a
```

### Example: Parsing a Function

```python
def Function():
    # Expected: 'func' Type Identifier '(' ParamListOpt ')' Block
    
    t = nextToken()
    if t[0] != 'func':
        fail('Expected func at start of function')
    
    typ = Type()  # Parse return type (e.g., 'int')
    
    idtok = nextToken()
    if idtok[0] != 'identifier':
        fail('Expected function name identifier')
    
    t = nextToken()
    if t[0] != 'lparen':
        fail('Expected ( after function name')
    
    params = ParamListOpt()  # Parse parameters
    
    t = nextToken()
    if t[0] != 'rparen':
        fail('Missing ) after parameter list')
    
    body = Block()  # Parse function body
    
    # Create AST node with function metadata
    return AST.Function(idtok[1], typ, params, body)
```

### Example: Parsing Expressions (Operator Precedence)

The **precedence climbing** technique is used:

```python
def Expr():
    return LogicalOr()  # Lowest precedence

def LogicalOr():
    left = LogicalAnd()
    return LogicalOrTail(left)

def LogicalOrTail(left):
    # LogicalOrTail → '||' LogicalAnd LogicalOrTail | ε
    la = lookahead()
    if la and la[0] == 'logop' and la[1] == '||':
        nextToken()  # Consume ||
        right = LogicalAnd()
        combined = AST.BinOp(left, '||', right)
        return LogicalOrTail(combined)  # Right-associative
    return left

# Similar functions for &&, ==, !=, <, >, <=, >=, +, -, *, /, %

def Unary():
    la = lookahead()
    if la and la[0] in ('unop', 'addop') and la[1] in ('-', '!', '~'):
        op = nextToken()[1]
        rhs = Unary()
        return AST.UnOp(op, rhs)
    return Primary()

def Primary():
    tok = nextToken()
    
    if tok[0] == 'number':
        return AST.Constant(tok[1])
    
    if tok[0] == 'identifier':
        symbol_ref = tok[3] if len(tok) > 3 else None
        if lookahead() and lookahead()[0] == 'lparen':
            # Function call
            nextToken()  # consume (
            args = ArgListOpt()
            nextToken()  # consume )
            return AST.FuncCall(tok[1], args, symbol_ref)
        else:
            # Variable reference
            return AST.Identifier(tok[1], symbol_ref)
```

### AST Node Classes (`ASTNodes.py`)

```python
class Function:
    def __init__(self, name, return_type, params, statement):
        self.name = name
        self.return_type = return_type
        self.params = params  # List of (type, name) tuples
        self.statement = statement  # Block

class BinOp:
    def __init__(self, left, oper, right):
        self.left = left    # Expression
        self.oper = oper    # '+', '-', '*', '==', etc.
        self.right = right   # Expression

class UnOp:
    def __init__(self, oper, inner_exp):
        self.oper = oper        # '-', '!', '~'
        self.inner_exp = inner_exp  # Expression

class Identifier:
    def __init__(self, name, symbol_ref=None):
        self.name = name
        self.symbol_ref = symbol_ref  # Mutable dict -> symbol table entry

class Constant:
    def __init__(self, value):
        self.value = value  # int, float, or boolean

class VarDecl:
    def __init__(self, typ, name, init=None):
        self.typ = typ      # Type name
        self.name = name    # Variable name
        self.init = init    # Optional initializer expression

class Assign:
    def __init__(self, target, expr):
        self.target = target  # Identifier
        self.expr = expr      # Expression
```

### Example AST Output

**Input Code:**
```c
func int add(int a, int b) {
    return a + b;
}
```

**Generated AST:**
```
Function(
    name='add',
    return_type='int',
    params=[(int, a), (int, b)],
    statement=Block([
        Return(
            BinOp(
                left=Identifier('a'),
                oper='+',
                right=Identifier('b')
            )
        )
    ])
)
```

---

## Stage 3: Semantic Analysis (`semantic.py`)

### Purpose
Verify that the code makes **semantic sense**:
- Variables are declared before use
- Types are compatible
- Function calls match signatures
- Control flow returns values

### Semantic Analyzer Structure

```python
class SemanticAnalyzer:
    def __init__(self):
        self.functions = {}  # function_name -> (return_type, params)
        self.scopes = []  # Stack of dicts for variable lookup
        self.current_function = None
        self.global_symbols = {}  # Global function symbols
        self.function_symbols = {}  # Per-function symbol tables
        self._next_addr = 0x1000  # Address allocator
```

### Two-Pass Analysis

**Pass 1: Collect Function Signatures**

```python
def analyze(self, program: AST.Program):
    funcs = program.getFunction()
    
    # First pass: collect function signatures
    for f in funcs:
        self.add_function(f.getName(), f.getReturnType(), f.getParams())
    
    # Second pass: analyze each function body
    for f in funcs:
        self.analyze_function(f)
    
    # Third pass: populate symbol references
    self.populate_symbol_refs(program)
```

This two-pass approach allows forward references (using a function before it's defined).

### Variable Declaration and Lookup

```python
def declare_var(self, name, typ, kind='local', init_value=None):
    """Declare a variable in the current scope"""
    scope = self.scopes[-1]  # Current lexical scope
    if name in scope:
        self.error(f"Duplicate declaration: '{name}'")
    scope[name] = typ
    
    # Allocate an address for this variable
    addr = self._alloc_addr()
    # Store symbol metadata
    self.global_symbols[name] = {
        'type': typ,
        'addr': addr,
        'additional': {...}
    }

def lookup_var(self, name):
    """Find a variable by searching scopes from innermost to outermost"""
    for scope in reversed(self.scopes):  # Search backward
        if name in scope:
            return scope[name]
    return None  # Not found
```

### Type Checking

```python
def type_of(self, node):
    """Determine the type of an expression"""
    t = type(node)
    
    if t is AST.Constant:
        if isinstance(node.value, bool):
            return 'bool'
        elif isinstance(node.value, float):
            return 'float'
        else:
            return 'int'
    
    if t is AST.Identifier:
        var_type = self.lookup_var(node.name)
        if var_type is None:
            self.error(f"Undeclared variable '{node.name}'")
        return var_type
    
    if t is AST.BinOp:
        left_t = self.type_of(node.left)
        right_t = self.type_of(node.right)
        
        # Arithmetic operators require numeric types
        if node.oper in ('+', '-', '*', '/', '%'):
            if left_t not in ('int', 'float') or right_t not in ('int', 'float'):
                self.error('Operator + requires numeric operands')
            # Float propagation: int + float = float
            if left_t == 'float' or right_t == 'float' or node.oper == '/':
                return 'float'
            return 'int'
        
        # Comparison operators return bool
        if node.oper in ('<', '>', '<=', '>=', '==', '!='):
            return 'bool'
```

### Statement Analysis

```python
def analyze_stmt(self, stmt):
    t = type(stmt)
    
    if t is AST.VarDecl:
        # Declare the variable
        init_type = None
        if stmt.init:
            init_type = self.type_of(stmt.init)
            # Check initializer type matches declaration
            if not self.is_assignable(stmt.typ, init_type):
                self.error(f"Type mismatch in initialization")
        self.declare_var(stmt.name, stmt.typ)
    
    if t is AST.Assign:
        # Check assignment is valid
        target_type = self.lookup_var(stmt.target.name)
        if target_type is None:
            self.error(f"Assignment to undeclared variable")
        expr_type = self.type_of(stmt.expr)
        if not self.is_assignable(target_type, expr_type):
            self.error(f"Type mismatch in assignment")
    
    if t is AST.IfElse:
        # If-condition must be boolean-compatible
        cond_type = self.type_of(stmt.cond)
        if not self.is_boolean_compatible(cond_type):
            self.error('If-condition must be boolean')
        self.analyze_block(stmt.then_branch)
        if stmt.else_branch:
            self.analyze_block(stmt.else_branch)
    
    if t is AST.Return:
        # Return type must match function return type
        expr_type = self.type_of(stmt.expression)
        expected = self.current_function.getReturnType()
        if not self.is_assignable(expected, expr_type):
            self.error(f"Return type mismatch")
```

### Type Compatibility

```python
def is_assignable(self, target_type, expr_type):
    """Check if expr_type can be assigned to target_type"""
    if target_type == expr_type:
        return True
    # Allow int -> float promotion
    if target_type == 'float' and expr_type == 'int':
        return True
    return False

def is_boolean_compatible(self, typ):
    """Check if a type can be used as a boolean"""
    return typ == 'bool' or typ in ('int', 'float')
```

### Symbol Reference Population

After semantic analysis, populate identifier nodes with symbol table references:

```python
def populate_symbol_refs(self, node):
    """Walk the AST and fill in symbol_ref dicts"""
    if node is None:
        return
    
    t = type(node)
    
    # For identifiers, resolve and store the symbol entry
    if t is AST.Identifier:
        if hasattr(node, 'symbol_ref') and node.symbol_ref is not None:
            entry = self.resolve_symbol_ref(node.name)
            if entry:
                node.symbol_ref['entry'] = entry
        return
    
    # For function calls, same thing
    if t is AST.FuncCall:
        if hasattr(node, 'symbol_ref') and node.symbol_ref is not None:
            entry = self.resolve_symbol_ref(node.name)
            if entry:
                node.symbol_ref['entry'] = entry
        for arg in node.args:
            self.populate_symbol_refs(arg)
        return
    
    # Recursively process child nodes
    # ... (process BinOp, UnOp, Block, etc.)
```

### Symbol Table Output

After analysis, print the collected symbol information:

```python
def print_symbol_tables(self):
    print("--- Symbol Tables ---\n")
    
    # Global symbols (functions)
    print("Globals:")
    print(f"{'Name':20} {'Type':12} {'Scope':8} {'Level':6} {'Address':12} {'Additional'}")
    for name, info in self.global_symbols.items():
        typ = info.get('type')
        addr = info.get('addr')
        additional = info.get('additional')
        print(f"{name:20} {typ:12} Global   -      {addr:12} {additional}")
    
    # Per-function symbols
    for func_name, scopes in self.function_symbols.items():
        print(f"\nFunction: {func_name}")
        for scope in scopes:
            label = scope.get('label', 'unknown')
            for var_name, var_info in scope['symbols'].items():
                typ = var_info['type']
                addr = var_info['addr']
                additional = var_info['additional']
                print(f"{var_name:20} {typ:12} {label:12} {addr:12} {additional}")
```

---

## Complete Compilation Pipeline

### Driver Program (`main.py`)

```python
def compile(contents):
    # Stage 1: Lexical Analysis
    token_list = lex(contents)
    print("--- Lexical analysis (tokens) ---")
    for t in token_list:
        print(t)
    
    # Stage 2: Syntax Analysis
    print("--- Syntax / AST ---")
    ast = lookaheadparser.parse(token_list)
    ast_tree_printer.pretty_print_ast_tree(ast)
    
    # Stage 3: Semantic Analysis
    print("--- Semantic Analysis ---")
    an = semantic.SemanticAnalyzer()
    try:
        an.analyze(ast)
        an.print_symbol_tables()
    except Exception:
        print("Semantic analysis failed")
        sys.exit(3)
```

### Example: Complete Compilation

**Input File: `test.c`**
```c
func int add(int a, int b) {
    return a + b;
}

func int main() {
    int x = 5;
    int y = 3;
    int result = add(x, y);
    return result;
}
```

**Stage 1 Output (Tokens):**
```
('func', 'func', 1)
('int', 'int', 1)
('identifier', 'add', 1, {})
('lparen', '(', 1)
('int', 'int', 1)
('identifier', 'a', 1, {})
...
```

**Stage 2 Output (AST):**
```
Program
├── Function: add
│   ├── return_type: int
│   ├── params: [(int, a), (int, b)]
│   └── Block
│       └── Return
│           └── BinOp: +
│               ├── Identifier: a
│               └── Identifier: b
└── Function: main
    ├── return_type: int
    └── Block
        ├── VarDecl: int x = 5
        ├── VarDecl: int y = 3
        ├── VarDecl: int result = add(x, y)
        └── Return Identifier: result
```

**Stage 3 Output (Symbol Table):**
```
--- Symbol Tables ---

Globals:
Name                 Type         Scope    Address  Additional
add                  function     Global   0x1000   returns=int, params=[('int', 'a'), ('int', 'b')]
main                 function     Global   0x1004   returns=int, params=[]

Function: add
Name                 Type         Scope        Address  Additional
a                    int          param        0x1008   kind=param
b                    int          param        0x100c   kind=param

Function: main
Name                 Type         Scope        Address  Additional
x                    int          local        0x1010   initialized=False
y                    int          local        0x1014   initialized=False
result               int          local        0x1018   initialized=False
```

---

## Key Design Decisions

### 1. Recursive Descent Parsing
- **Why?** Simple, intuitive, easy to implement and debug
- **Trade-off:** Slightly less efficient than LR parsers, but adequate for small programs

### 2. Two-Pass Semantic Analysis
- **Why?** Allows forward references (calling functions before declaration)
- **Pass 1:** Collect all function signatures
- **Pass 2:** Validate bodies against signatures

### 3. Symbol Reference in Tokens
- **Why?** Makes it easy for downstream tools to access symbol information
- **How?** Each identifier token carries a mutable dict that semantic analyzer fills in
- **Benefit:** No need to re-lookup symbols; just access the dict

### 4. Lexical Scoping with Stack
- **Why?** Correctly models nested scopes (functions, blocks, loops)
- **How?** `scopes` is a list of dicts; innermost scope is at the end
- **Lookup:** Search from innermost to outermost

---

## Error Handling

The compiler detects and reports three main categories of errors:

### 1. Syntax Errors
```python
def fail(err):
    print('ERROR ' + err)
    sys.exit()

# Example usage:
if t[0] != 'lparen':
    fail('Expected ( after function name')
```

### 2. Semantic Errors
```python
def error(self, msg):
    print('Semantic ERROR: ' + msg)
    raise SemanticError(msg)

# Example usage:
if self.lookup_var(name) is None:
    self.error(f"Undeclared variable '{name}'")
```

### 3. Type Errors
```python
# Operator type checking
if left_t not in ('int', 'float') or right_t not in ('int', 'float'):
    self.error('Operator + requires numeric operands')

# Assignment type checking
if not self.is_assignable(target_type, expr_type):
    self.error('Type mismatch in assignment')
```

---

## Testing Examples

### Test 1: Valid Program
```c
func int main() {
    int x = 10;
    return x;
}
```
✅ **Result:** Success, symbol table populated

### Test 2: Type Error
```c
func int main() {
    int x = 5;
    int y = x + true;  // ERROR: can't add int and bool
    return 0;
}
```
❌ **Result:** "Semantic ERROR: Operator + requires numeric operands"

### Test 3: Undeclared Variable
```c
func int main() {
    return z;  // ERROR: z not declared
}
```
❌ **Result:** "Use of undeclared variable 'z'"

### Test 4: Complex Expressions
```c
func int main() {
    int a = 5;
    int b = 3;
    int result = (a + b) * 2 - 1;  // Complex expression
    return result;
}
```
✅ **Result:** Correct operator precedence: ((a + b) * 2) - 1

---

## Summary Table

| Component | Input | Output | Key Function |
|-----------|-------|--------|--------------|
| **Lexer** | Source code (text) | Token stream (4-tuples) | `lex()`, `check()` |
| **Parser** | Token stream | Abstract Syntax Tree | Recursive descent functions |
| **Semantic Analyzer** | AST | Validated AST + Symbol Table | `analyze()`, `analyze_stmt()` |
| **Pretty Printer** | AST | Formatted tree output | `pretty_print_ast_tree()` |

---

## Viva Tips

1. **Know the three stages:** Lexical → Syntax → Semantic
2. **Understand operator precedence:** Lower operators parsed deeper in recursion
3. **Symbol tables are key:** Every identifier needs an entry with type, address, scope
4. **Two-pass for forward references:** First collect signatures, then validate bodies
5. **Type compatibility rules:** int → float allowed, but not reverse
6. **Scope management:** Stack of dicts, innermost takes precedence

Good luck with your viva! 🎯
