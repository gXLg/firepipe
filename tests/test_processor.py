from firepipe.lexing.token_types import (
  SymbolTokenType, IntegerTokenType,
  WhiteSpaceTokenType
)
from firepipe.lexing.types import Token

from firepipe.parsing.rules import (
  Op, Or, Ordered, Syntax
)
from firepipe.parsing.aliases import (
  BinInfLeft, UnPref, Brackets
)

from firepipe.processing.types import Node, Operator
from firepipe.processing.processor import Processor, ProcessorFrame

from firepipe.typing import RuntimeType, DefaultSelector
from firepipe.pipeline.env import Env


class TestEnv(Env):
  def handle(self, res):
    pass

class RunInt(RuntimeType):
  def plus(self, n, e, a, b):
    return a + b

  def minus(self, n, e, a, b):
    return a - b

  def mul(self, n, e, a, b):
    return a * b

  def uminus(self, n, e, a):
    return -a

run_int = RunInt()
selector = DefaultSelector(run_int)

PLUS = SymbolTokenType("+")
MINUS = SymbolTokenType("-")
MUL = SymbolTokenType("*")
LBR = SymbolTokenType("(")
RBR = SymbolTokenType(")")
NUM = IntegerTokenType()
SPACE = WhiteSpaceTokenType()

OP_PLUS = Op(PLUS, 2, selector, "plus")
OP_MINUS = Op(MINUS, 2, selector, "minus")
OP_MUL = Op(MUL, 2, selector, "mul")
OP_UMINUS = Op(MINUS, 1, selector, "uminus")

rules = {
  "$": Ordered("sum"),
  "sum": BinInfLeft("product", Or(OP_PLUS, OP_MINUS)),
  "product": BinInfLeft("factor", OP_MUL),
  "factor": Or("brackets", "unary", NUM),
  "brackets": Brackets(LBR, "sum", RBR),
  "unary": UnPref(OP_UMINUS, "factor")
}

proc = Processor(TestEnv())

# ---

tok = [
  Token("123", 0, NUM), Token("*", 4, MUL),
  Token("(", 6, LBR), Token("0", 7, NUM),
  Token("+", 10, PLUS), Token("1", 11, NUM),
  Token(")", 12, RBR), Token("-", 13, MINUS),
  Token("5", 15, NUM)
]
sum = Node(
  args=[Node(args=[tok[3]]), Node(args=[tok[5]])],
  ops=[Operator(tok[4], 2, selector, "plus")]
)
prod = Node(
  args=[Node(args=[tok[0]]), sum],
  ops=[Operator(tok[1], 2, selector, "mul")]
)
node = Node(
  args=[prod, Node(args=[tok[8]])],
  ops=[Operator(tok[7], 2, selector, "minus")]
)
f = ProcessorFrame(node)
res = proc.process(f)
exp = 123 * (1 + 0) - 5

assert res == exp
