from typing import Iterable, Any

from .types import Token, AbstractTokenType
from ..utils import IndexedView, reduce


class SymbolTokenType(AbstractTokenType):
  def __init__(self, symbol: str):
    super().__init__()
    self.symbol = symbol
    self.len = len(symbol)

  def lex(self, iview: IndexedView) -> Token | None:
    pos = iview.index
    string = iview.peek(self.len)
    if string == self.symbol:
      iview.step(self.len)
      return Token(string, pos, self)

  def prepare(self, token: Token) -> str:
    return token.string

  def __reduce__(self):
    return reduce(self, (self.symbol,))

  def __str__(self):
    return f"Symbol({self.symbol})"

class IntegerTokenType(AbstractTokenType):
  def __init__(self):
    super().__init__()

  def lex(self, iview: IndexedView) -> Token | None:
    iview.save()
    pos = iview.index
    n = ""
    while not iview.done():
      k = iview.peek(1)[0]
      if not k.isnumeric(): break
      if n == "0":
        n = ""
        break
      n += k
      iview.step(1)

    if n:
      iview.discard()
      return Token(n, pos, self)

    iview.restore()

  def prepare(self, token: Token) -> int:
    return int(token.string)

  def __str__(self):
    return "Int()"

class IgnoreTokenType(AbstractTokenType):
  def __init__(self, ignore_list: Iterable[AbstractTokenType]):
    super().__init__()
    self.list = ignore_list

  def lex(self, iview: IndexedView):
    while any(ttype.lex(iview) is not None for ttype in self.list):
      pass

  def prepare(self, token: Token):
    return None

  def __reduce__(self):
    return reduce(self, (tuple(self.ignore_list),))

  def __str__(self):
    return f"Ignore({', '.join(map(str, self.list))})"

class WhiteSpaceTokenType(IgnoreTokenType):
  def __init__(self):
    super().__init__([
      SymbolTokenType(" "),
      SymbolTokenType("\n"),
      SymbolTokenType("\t"),
      SymbolTokenType("\v")
    ])

  def __reduce__(self):
    return reduce(self)

  def __str__(self):
    return "Space()"

class LetterTokenType(AbstractTokenType):
  def __init__(self):
    super().__init__()

  def lex(self, iview: IndexedView):
    pos = iview.index
    string = iview.peek(1)
    if string.isascii() and string.isalpha():
      iview.step(1)
      return Token(string, pos, self)

  def prepare(self, token: Token) -> str:
    return token.string

  def __str__(self):
    return "Letter()"
