#!/usr/bin/env python3
"""Quick test to verify symbol_ref population in identifier tokens."""

from lexer import lex
import lookaheadparser
import semantic
import ASTNodes

source = '''
func int test(int x) {
    int y = 5;
    return x;
}
'''

tokens = lex(source)
ast = lookaheadparser.parse(tokens)
an = semantic.SemanticAnalyzer()
an.analyze(ast)

# Find first identifier node and check if symbol_ref is populated
def find_identifier(node):
    if isinstance(node, ASTNodes.Identifier):
        return node
    t = type(node)
    if t is ASTNodes.BinOp:
        r = find_identifier(node.left)
        if r: return r
        return find_identifier(node.right)
    if t is ASTNodes.Function:
        return find_identifier(node.statement)
    if t is ASTNodes.Block:
        for s in node.statements:
            r = find_identifier(s)
            if r: return r
    if t is ASTNodes.Return:
        return find_identifier(node.expression)
    if t is ASTNodes.VarDecl:
        if node.init:
            return find_identifier(node.init)
    if t is ASTNodes.Assign:
        r = find_identifier(node.target)
        if r: return r
        return find_identifier(node.expr)
    if t is ASTNodes.Program:
        for f in node.getFunction():
            r = find_identifier(f)
            if r: return r
    return None

ident = find_identifier(ast)
if ident:
    print(f'Found identifier: {ident.name}')
    print(f'symbol_ref dict: {ident.symbol_ref}')
    if ident.symbol_ref and 'entry' in ident.symbol_ref:
        print(f'Symbol entry found: {ident.symbol_ref["entry"]}')
    else:
        print("symbol_ref is empty or has no 'entry' key")
else:
    print("No identifier found in AST")
