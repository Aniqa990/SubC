keywords = ["auto", "struct", "break", "else", "switch", "case", "enum", "register", "typedef", "extern", "return", "union", "const", "unsigned", "continue", "for", "signed", "void" , "default", "sizeof", "volatile" , "do", "if", "static", "while", "true", "false", "print", "read", "func"]
types = ["double", "int", "long", "char", "float", "short", "bool"] 

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

		# two-character operators
		if c == '=' and nxt == '=':
			token_list.append(("Operator", '==', lineNumber)); x += 2; continue
		if c == '!' and nxt == '=':
			token_list.append(("Operator", '!=', lineNumber)); x += 2; continue
		if c == '<' and nxt == '=':
			token_list.append(("Operator", '<=', lineNumber)); x += 2; continue
		if c == '>' and nxt == '=':
			token_list.append(("Operator", '>=', lineNumber)); x += 2; continue
		if c == '&' and nxt == '&':
			token_list.append(("Operator", '&&', lineNumber)); x += 2; continue
		if c == '|' and nxt == '|':
			token_list.append(("Operator", '||', lineNumber)); x += 2; continue

		# single-character tokens
		if c == '=':
			token_list.append(("Assign", '=', lineNumber)); x += 1; continue
		if c in '+-*/%~':
			token_list.append(("Operator", c, lineNumber)); x += 1; continue
		if c in '<>':
			token_list.append(("Operator", c, lineNumber)); x += 1; continue
		if c == '(':
			token_list.append(("Open-Paren", c, lineNumber)); x += 1; continue
		if c == ')':
			token_list.append(("Close-Paren", c, lineNumber)); x += 1; continue
		if c == '{':
			token_list.append(("Open-Brace", c, lineNumber)); x += 1; continue
		if c == '}':
			token_list.append(("Close-Brace", c, lineNumber)); x += 1; continue
		if c == ';':
			token_list.append(("Semicolon", c, lineNumber)); x += 1; continue
		if c == ',':
			token_list.append(("Comma", c, lineNumber)); x += 1; continue

		# unknown/ignored characters - skip
		x += 1
	
	# filter returns an iterator in Python 3 — convert to list so callers can index/slice
	return list(filter(None, token_list))

def check(newStr):
	if newStr == '' or newStr == '\n':
		return None
	elif newStr in keywords:
		# classify true/false as Boolean for convenience
		if newStr == 'true' or newStr == 'false':
			return ("Boolean", newStr, lineNumber)
		return ("Keyword", newStr, lineNumber)
	elif newStr in types:
		return ("Type", newStr, lineNumber)
	# numeric literal detection (integer or float)
	elif newStr.replace('.', '', 1).isdigit() and newStr.count('.') <= 1 and newStr != '.':
		if '.' in newStr:
			return ("Float", newStr, lineNumber)
		return ("Integer", newStr, lineNumber)
	elif len(newStr) > 0 and len(newStr) < 32:
		return ("Identifier", newStr, lineNumber)