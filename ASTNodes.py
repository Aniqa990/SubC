class Constant():
	
	value = 0
	
	def __init__(self, value):
		self.value = value

	def getValue(self):
		return self.value

	def __repr__(self):
		return f"Constant({self.value})"

	def is_boolean(self):
		return str(self.value) in ('true', 'false')

	def is_float(self):
		try:
			return '.' in str(self.value)
		except:
			return False

	def next(self):
		return False

class Return():

	expression = ""

	def __init__(self, expression):
		self.expression = expression

	def getExpression(self):
		return self.expression

	def __repr__(self):
		return f"Return({repr(self.expression)})"

	def next(self):
		return self.expression

class Function():
	name = ""
	statement = 0
	return_type = None
	params = None

	def __init__(self, name, return_type, params, statement):
		self.name = name
		self.return_type = return_type
		# params is a list of (type, name) tuples
		self.params = params or []
		self.statement = statement

	def getName(self):
		return self.name

	def getStatement(self):
		return self.statement

	def getReturnType(self):
		return self.return_type

	def getParams(self):
		return self.params

	def __repr__(self):
		return f"Function(name={self.name!r}, return_type={self.return_type!r}, params={self.params!r}, stmt={repr(self.statement)})"

class Program():

	function_declaration = 0

	def __init__(self, func):
		self.function_declaration = func

	def getFunction(self):
		return self.function_declaration

	def getNext(self):
		return self.function_declaration

	def __repr__(self):
		return f"Program({repr(self.function_declaration)})"

class UnOp():

	oper = ""
	inner_exp = ""

	def __init__(self, oper, inner_exp):
		self.oper = oper
		self.inner_exp = inner_exp

	def getExpression(self):
		return self.inner_exp

	def getOperator(self):
		return self.oper

	def next(self):
		if isinstance(self.inner_exp, UnOp):
			return self.inner_exp
		else:
			return False

	def __repr__(self):
		return f"UnOp({self.oper!r}, {repr(self.inner_exp)})"

	# keep compatibility

class Identifier:

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return f"Identifier({self.name!r})"


class BinOp:

	def __init__(self, left, oper, right):
		self.left = left
		self.oper = oper
		self.right = right

	def __repr__(self):
		return f"BinOp({repr(self.left)}, {self.oper!r}, {repr(self.right)})"


class VarDecl:

	def __init__(self, typ, name, init=None):
		self.typ = typ
		self.name = name
		self.init = init

	def __repr__(self):
		return f"VarDecl(type={self.typ!r}, name={self.name!r}, init={repr(self.init)})"


class Assign:

	def __init__(self, target, expr):
		self.target = target
		self.expr = expr

	def __repr__(self):
		return f"Assign({repr(self.target)}, {repr(self.expr)})"


class Block:

	def __init__(self, statements=None):
		self.statements = statements or []

	def __repr__(self):
		return f"Block({repr(self.statements)})"


class IfElse:

	def __init__(self, cond, then_branch, else_branch=None):
		self.cond = cond
		self.then_branch = then_branch
		self.else_branch = else_branch

	def __repr__(self):
		return f"IfElse(cond={repr(self.cond)}, then={repr(self.then_branch)}, else={repr(self.else_branch)})"


class While:

	def __init__(self, cond, body):
		self.cond = cond
		self.body = body

	def __repr__(self):
		return f"While(cond={repr(self.cond)}, body={repr(self.body)})"


class For:

	def __init__(self, init, cond, step, body):
		self.init = init
		self.cond = cond
		self.step = step
		self.body = body

	def __repr__(self):
		return f"For(init={repr(self.init)}, cond={repr(self.cond)}, step={repr(self.step)}, body={repr(self.body)})"


class FuncCall:

	def __init__(self, name, args=None):
		self.name = name
		self.args = args or []

	def __repr__(self):
		return f"FuncCall({self.name!r}, args={repr(self.args)})"


class Print:

	def __init__(self, expr):
		self.expr = expr

	def __repr__(self):
		return f"Print({repr(self.expr)})"


class Read:

	def __init__(self, target):
		self.target = target

	def __repr__(self):
		return f"Read({repr(self.target)})"
