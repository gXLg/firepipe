from ..utils import IndexedView, reduce, setstate
from .types import IgnoreTokenType


class Lexer:
  def __init__(self, ttypes):
    self.types = []
    self.ignore_types = []
    for ttype in ttypes:
      if isinstance(ttype, IgnoreTokenType):
        self.ignore_types.append(ttype)
      else:
        self.types.append(ttype)

  def lex(self, view):
    iview = IndexedView(view)
    tokens = []
    while not iview.done():
      for ttype in self.ignore_types:
        ttype.lex(iview)
      if iview.done(): break
      for ttype in self.types:
        res = ttype.lex(iview)
        if res is not None:
          tokens.append(res)
          break
      else:
        raise Exception(f"Unknown token: '{iview.peek(5)}...' at {iview.index}")
    return tokens

  def __reduce__(self):
    return reduce(self, ((),), ("types", "ignore_types"))

  def __setstate__(self, state):
    setstate(self, state)
