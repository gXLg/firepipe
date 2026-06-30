#import pickle

from sdparser.lexing.token_types import (
  SymbolTokenType, IntegerTokenType, WhiteSpaceTokenType
)
from sdparser.parsing.rules import (
  Op, ArgOp, Or, Ordered, Syntax, Star
)

from sdparser.lexing.lexer import Lexer
from sdparser.parsing.parser import Parser, ParseFrame
from sdparser.runtime.runner import Runner, Frame
from sdparser.typing import RuntimeType, DefaultSelector


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

OP_PLUS = Op(PLUS, 2, type_selector, "_op_plus")
OP_MINUS = Op(MINUS, 2, type_selector, "_op_minus")
OP_MUL = Op(MUL, 2, type_selector, "_op_mul")
OP_DIV = Op(DIV, 2, type_selector, "_op_div")
OP_UPLUS = Op(PLUS, 1, type_selector, "_op_uplus")
OP_UMINUS = Op(MINUS, 1, type_selector, "_op_uminus")
OP_LAST = ArgOp(LAST, type_selector, "_arg_last")

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
