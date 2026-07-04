from firepipe.lexing.token_types import (
  SymbolTokenType, IntegerTokenType,
  WhiteSpaceTokenType, LetterTokenType
)
from firepipe.parsing.rules import (
  Op, ArgOp, Or, Ordered, Syntax, Star, Repeat
)
from firepipe.typing import RuntimeType, DefaultSelector
from firepipe.pipeline.machine import Machine
from firepipe.pipeline.machine import Env


class VarEnv(Env):
  def __init__(self):
    super().__init__()

  def handle(self, res):
    self.content["last"] = res

  def get_last(self):
    return self.get_var("last")

  def get_var(self, var):
    return self.content.get(var, 0)

  def set_var(self, var, val):
    self.content[var] = val

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

  def _op_assign(self, n, e, a, b):
    e.set_var(a, b)
    return b

  def _arg_last(self, n, e):
    return e.get_last()

  def _arg_var(self, n, e):
    return e.get_var(n.string)

type_instance = OnePiece()
type_selector = DefaultSelector(type_instance)

PLUS = SymbolTokenType("+")
MINUS = SymbolTokenType("-")
MUL = SymbolTokenType("*")
DIV = SymbolTokenType("/")
LBR = SymbolTokenType("(")
RBR = SymbolTokenType(")")
LAST = SymbolTokenType("_")
ASSIGN = SymbolTokenType("=")
VAR = LetterTokenType()
NUM = IntegerTokenType()
SPACE = WhiteSpaceTokenType()

all_tokens = [
  PLUS, MINUS, MUL, DIV,
  ASSIGN, LBR, RBR,
  SPACE, LAST, NUM, VAR
]

OP_PLUS = Op(PLUS, 2, type_selector, "_op_plus")
OP_MINUS = Op(MINUS, 2, type_selector, "_op_minus")
OP_MUL = Op(MUL, 2, type_selector, "_op_mul")
OP_DIV = Op(DIV, 2, type_selector, "_op_div")
OP_UPLUS = Op(PLUS, 1, type_selector, "_op_uplus")
OP_UMINUS = Op(MINUS, 1, type_selector, "_op_uminus")
OP_ASSIGN = Op(ASSIGN, 2, type_selector, "_op_assign")
ARG_LAST = ArgOp(LAST, type_selector, "_arg_last")
ARG_VAR = ArgOp(VAR, type_selector, "_arg_var")

calc_rules = {
  "$": Ordered("assign"),
  "assign": Or(Ordered(VAR, OP_ASSIGN, "assign"), "sum"),
  "sum": Ordered("product", Star(Or(OP_PLUS, OP_MINUS), "product")),
  "product": Ordered("factor", Star(Or(OP_MUL, OP_DIV), "factor")),
  "factor": Or("brackets", "unary", NUM, ARG_LAST, ARG_VAR),
  "brackets": Ordered(Syntax(LBR), "assign", Syntax(RBR)),
  "unary": Ordered(Or(OP_UPLUS, OP_UMINUS), "factor")
}

def create_calculator():
  return Machine(all_tokens, calc_rules, VarEnv())
