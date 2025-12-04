keywords = ["auto", "struct", "break", "else", "switch", "case", "enum", "register", "typedef", "extern", "return", "union", "const", "unsigned", "continue", "for", "signed", "void" , "default", "sizeof", "volatile" , "do", "if", "static", "while", "true", "false", "print", "read", "func"]
types = ["double", "int", "long", "char", "float", "short", "bool", "void"] 

'''
Produces a stream of tokens.
Current terminals: Keyword, Identifier, Open-Paren, Closed-Paren, Open-Brace, Closed-Brace, Semicolon, Integer
'''
lineNumber = 1

def lex(source):	
	token_list = []
	x = 0
	newStr = ""
	global lineNumber
	while x < len(source):
		c = source[x]

		# Collect identifiers, numbers, dots (for floats), and underscores
		if c.isalpha() or c.isdigit() or c == '_' or c == '.':
			newStr += c
			x += 1
			continue

		# whitespace
		if c.isspace():
			token_list.append(check(newStr))
			newStr = ""
			if c == '\n':
				lineNumber += 1
			x += 1
			continue

		# punctuation / operators
		# flush any running identifier/number
		token_list.append(check(newStr))
		newStr = ""

		nxt = source[x+1] if x+1 < len(source) else ''

		# comments: skip // ... until end of line
		if c == '/' and nxt == '/':
			while x < len(source) and source[x] != '\n':
				x += 1
			continue

		# two-character operators
		if c == '=' and nxt == '=':
			token_list.append(("relop", '==', lineNumber)); x += 2; continue
		if c == '!' and nxt == '=':
			token_list.append(("relop", '!=', lineNumber)); x += 2; continue
		if c == '<' and nxt == '=':
			token_list.append(("relop", '<=', lineNumber)); x += 2; continue
		if c == '>' and nxt == '=':
			token_list.append(("relop", '>=', lineNumber)); x += 2; continue
		if c == '&' and nxt == '&':
			token_list.append(("logop", '&&', lineNumber)); x += 2; continue
		if c == '|' and nxt == '|':
			token_list.append(("logop", '||', lineNumber)); x += 2; continue

		# single-character tokens
		if c == '=':
			token_list.append(("assign", '=', lineNumber)); x += 1; continue
		if c in '+-':
			token_list.append(("addop", c, lineNumber)); x += 1; continue
		if c == '*':
			token_list.append(("mulop", c, lineNumber)); x += 1; continue
		if c == '/':
			token_list.append(("divop", c, lineNumber)); x += 1; continue
		if c == '%':
			token_list.append(("modop", c, lineNumber)); x += 1; continue
		if c == '~' or c == '!':
			token_list.append(("unop", c, lineNumber)); x += 1; continue
		if c in '<>':
			token_list.append(("relop", c, lineNumber)); x += 1; continue
		if c == '(':
			token_list.append(("lparen", c, lineNumber)); x += 1; continue
		if c == ')':
			token_list.append(("rparen", c, lineNumber)); x += 1; continue
		if c == '{':
			token_list.append(("lbrace", c, lineNumber)); x += 1; continue
		if c == '}':
			token_list.append(("rbrace", c, lineNumber)); x += 1; continue
		if c == ';':
			token_list.append(("semicolon", c, lineNumber)); x += 1; continue
		if c == ',':
			token_list.append(("comma", c, lineNumber)); x += 1; continue

		# unknown/ignored characters - skip
		x += 1
	
	# filter returns an iterator in Python 3 — convert to list so callers can index/slice
	return list(filter(None, token_list))

def check(newStr):
	if newStr == '' or newStr == '\n':
		return None

	# Keywords: emit the keyword itself as the token type (e.g. 'for', 'if')
	if newStr in keywords:
		return (newStr, newStr, lineNumber)

	# Types: emit the type name as the token type (e.g. 'int', 'float')
	if newStr in types:
		return (newStr, newStr, lineNumber)

	# numeric literal detection (integer or float) -> emit ('number', value)
	if newStr.replace('.', '', 1).isdigit() and newStr.count('.') <= 1 and newStr != '.':
		try:
			if '.' in newStr:
				return ("number", float(newStr), lineNumber)
			return ("number", int(newStr), lineNumber)
		except Exception:
			return ("number", newStr, lineNumber)

	# identifier: emit ('identifier', name, lineNumber, symbol_ref)
	# symbol_ref is a mutable container (dict) that the semantic analyzer will populate
	if len(newStr) > 0 and len(newStr) < 32:
		symbol_ref = {}  # Mutable dict; semantic analyzer will fill in {'entry': symbol_table_entry}
		return ("identifier", newStr, lineNumber, symbol_ref)

	return None