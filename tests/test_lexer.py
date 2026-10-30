from firepipe.lexing.token_types import (
  SymbolTokenType, IntegerTokenType,
  WhiteSpaceTokenType
)
from firepipe.lexing.types import Token, LexerError
from firepipe.lexing.lexer import Lexer


PLUS = SymbolTokenType("+")
MINUS = SymbolTokenType("-")
MUL = SymbolTokenType("*")
LBR = SymbolTokenType("(")
RBR = SymbolTokenType(")")
NUM = IntegerTokenType()
SPACE = WhiteSpaceTokenType()

all_tokens = [PLUS, MINUS, MUL, LBR, RBR, SPACE, NUM]

lexer = Lexer(all_tokens)

# ---

res = lexer.lex("")
assert res == []

# ---

res = lexer.lex("123 * (0  +1)- 5")
exp = [
  Token("123", 0, NUM), Token("*", 4, MUL),
  Token("(", 6, LBR), Token("0", 7, NUM),
  Token("+", 10, PLUS), Token("1", 11, NUM),
  Token(")", 12, RBR), Token("-", 13, MINUS),
  Token("5", 15, NUM)
]
assert len(res) == len(exp)

for r, e in zip(res, exp):
  assert r.string == e.string
  assert r.pos == e.pos
  assert r.type == e.type

# ---

try:
  lexer.lex("g")
  assert False
except LexerError:
  assert True
