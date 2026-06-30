from sdparser.lexing.types import (
  SymbolTokenType, IntegerTokenType, WhiteSpaceTokenType
)
from sdparser.parsing.rules import (
  Or, Ordered, Syntax, Star
)

from sdparser.lexing.lexer import Lexer
from sdparser.parsing.parser import Parser, ParseFrame
from sdparser.executing.runner import Runner, Frame
from sdparser.executing.runtime import RuntimeType, DefaultSelector

#import pickle

class OnePiece(RuntimeType):
  def __init__(self):
    super().__init__()

  def _op_plus(self, n, e, a, b):
    return a + b

  def _op_minus(self, n, e, a, b):
    return a - b

  def _op_mul(self, n, e, a, b):
    return a * b

  def _op_div(self, n, e, a, b):
    return a // b

  def _op_uplus(self, n, e, a):
    return a

  def _op_uminus(self, n, e, a):
    return -a

  def _arg_last(self, n, e):
    return e.get("last", 0)

type_instance = OnePiece()
type_selector = DefaultSelector(type_instance)

PLUS = SymbolTokenType("+")
MINUS = SymbolTokenType("-")
MUL = SymbolTokenType("*")
DIV = SymbolTokenType("/")
LBR = SymbolTokenType("(")
RBR = SymbolTokenType(")")
LAST = SymbolTokenType("_")
NUM = IntegerTokenType()
SPACE = WhiteSpaceTokenType()
all_tokens = [PLUS, MINUS, MUL, DIV, LBR, RBR, SPACE, LAST, NUM]

OP_PLUS = type_selector.create_op(PLUS, 2, "plus")
OP_MINUS = type_selector.create_op(MINUS, 2, "minus")
OP_MUL = type_selector.create_op(MUL, 2, "mul")
OP_DIV = type_selector.create_op(DIV, 2, "div")
OP_UPLUS = type_selector.create_op(PLUS, 1, "uplus")
OP_UMINUS = type_selector.create_op(MINUS, 1, "uminus")
OP_LAST = type_selector.create_arg_op(LAST, "last")

calc_rules = {
  "$": Ordered("sum"),
  "factor": Or("brackets", "unary", NUM, OP_LAST),
  "brackets": Ordered(Syntax(LBR), "sum", Syntax(RBR)),
  "unary": Ordered(Or(OP_UPLUS, OP_UMINUS), "factor"),
  "sum": Ordered("product", Star(Or(OP_PLUS, OP_MINUS), "product")),
  "product": Ordered("factor", Star(Or(OP_MUL, OP_DIV), "factor"))
}

class Calculator:
  def __init__(self):
    self.lexer = Lexer(all_tokens)
    self.parser = Parser(calc_rules)
    self.env = {}
    self.runner = Runner(self.env)

  def calc(self, expr):
    tokens = self.lexer.lex(expr)

    parse_frame = ParseFrame(self.parser.init)
    #parse_frame = pickle.loads(pickle.dumps(parse_frame))
    node = self.parser.parse(tokens, parse_frame)

    frame = Frame(node)
    #frame = pickle.loads(pickle.dumps(frame))
    res = self.runner.run(frame)

    self.env["last"] = res
    return res

if __name__ == "__main__":
  print("Simple Integer Calculator")
  calc = Calculator()
  while True:
    try:
      expr = input("> ")
    except EOFError: break
    if not expr: break
    print(calc.calc(expr))
    print()

  print("Bye!")
