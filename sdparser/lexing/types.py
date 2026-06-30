from ..utils import reduce
from .token import Token


class AbstractTokenType:
  def lex(self, iview):
    raise NotImplementedError

  def prepare(self, token):
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self)

  def __str__(self):
    return "Rule()"

class SymbolTokenType(AbstractTokenType):
  def __init__(self, symbol):
    super().__init__()
    self.symbol = symbol
    self.len = len(symbol)

  def lex(self, iview):
    pos = iview.index
    string = iview.peek(self.len)
    if string == self.symbol:
      iview.step(self.len)
      return Token(string, pos, self)

  def prepare(self, token):
    return token.string

  def __reduce__(self):
    return reduce(self, (self.symbol,))

  def __str__(self):
    return f"Symbol({self.symbol})"

class IntegerTokenType(AbstractTokenType):
  def __init__(self):
    super().__init__()

  def lex(self, iview):
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

  def prepare(self, token):
    return int(token.string)

  def __str__(self):
    return "Int()"

class IgnoreTokenType(AbstractTokenType):
  def __init__(self, ignore_list):
    super().__init__()
    self.list = ignore_list

  def lex(self, iview):
    while any(ttype.lex(iview) is not None for ttype in self.list):
      pass

  def prepare(self, token):
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

  def __str__(self):
    return "Space()"
