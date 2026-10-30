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
from firepipe.parsing.types import ParserError
from firepipe.parsing.parser import Parser, ParseFrame

from firepipe.processing.types import Node, Operator


PLUS = SymbolTokenType("+")
MINUS = SymbolTokenType("-")
MUL = SymbolTokenType("*")
LBR = SymbolTokenType("(")
RBR = SymbolTokenType(")")
NUM = IntegerTokenType()
SPACE = WhiteSpaceTokenType()

OP_PLUS = Op(PLUS, 2, None, "plus")
OP_MINUS = Op(MINUS, 2, None, "minus")
OP_MUL = Op(MUL, 2, None, "mul")
OP_UMINUS = Op(MINUS, 1, None, "uminus")

rules = {
  "$": Ordered("sum"),
  "sum": BinInfLeft("product", Or(OP_PLUS, OP_MINUS)),
  "product": BinInfLeft("factor", OP_MUL),
  "factor": Or("brackets", "unary", NUM),
  "brackets": Brackets(LBR, "sum", RBR),
  "unary": UnPref(OP_UMINUS, "factor")
}

parser = Parser(rules)

# ---

f = ParseFrame(parser.init)
tok = [
  Token("123", 0, NUM), Token("*", 4, MUL),
  Token("(", 6, LBR), Token("0", 7, NUM),
  Token("+", 10, PLUS), Token("1", 11, NUM),
  Token(")", 12, RBR), Token("-", 13, MINUS),
  Token("5", 15, NUM)
]
res = parser.parse(tok, f)

sum = Node(
  args=[Node(args=[tok[3]]), Node(args=[tok[5]])],
  ops=[Operator(tok[4], 2, None, "plus")]
)
prod = Node(
  args=[Node(args=[tok[0]]), sum],
  ops=[Operator(tok[1], 2, None, "mul")]
)
exp = Node(
  args=[prod, Node(args=[tok[8]])],
  ops=[Operator(tok[7], 2, None, "minus")]
)

assert str(res) == str(exp)

# ---

f = ParseFrame(parser.init)
try:
  parser.parse([], f)
  assert False
except ParserError:
  assert True
