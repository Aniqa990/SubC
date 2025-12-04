import sys
from lexer import lex
import lookaheadparser

'''
Rules For Identifiers:
	They must begin with a letter or underscore(_).
	They must consist of only letters, digits, or underscore. No other special character is allowed.
	It should not be a keyword.
	It must not contain white space.
	It should be up to 31 characters long as only first 31 characters are significant.
'''

'''
Accepts C program from user, reads it and passes it to lexer for lexical analysis.
'''
def main():
	# Require a source file argument; show usage if missing
	if len(sys.argv) < 2:
		print("Usage: python main.py <source_file.c>")
		print("Example: python main.py \"Test Programs/return_1.c\"")
		sys.exit(2)

	source_file = sys.argv[1]
	if check_file(source_file):
		with open(source_file, "r") as f:
			contents = f.read()
			compile(contents)

'''
Produces a token list by calling the lexer and uses the token list to produce an abstract syntax tree.
'''
def compile(contents):
	token_list = lex(contents)
	# Show lexer output (tokens)
	print("--- Lexical analysis (tokens) ---")
	for t in token_list:
		# Remove symbol_ref dict (4th element) from identifier tokens for cleaner output
		if len(t) == 4 and t[0] == 'identifier':
			print((t[0], t[1], t[2]))
		else:
			print(t)
	print("--- End tokens ---\n")

	# Parse and show AST
	print("--- Syntax / AST ---")
	ast = lookaheadparser.parse(token_list)
	import ast_tree_printer
	ast_tree_printer.pretty_print_ast_tree(ast)
	print("--- End AST ---")

	# Semantic analysis
	import semantic
	an = semantic.SemanticAnalyzer()
	try:
		an.analyze(ast)
		# print symbol tables after successful analysis
		an.print_symbol_tables()
	except Exception:
		print("Semantic analysis failed")
		sys.exit(3)

'''
Checks if .c file is passed to the compiler. 
'''
def check_file(source_file):
	if not source_file.rstrip().endswith('.c'):
		print ("ERR: not a valid .c file")
		return False
	return True

if __name__=='__main__':
	main()











