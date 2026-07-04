from __future__ import annotations
from typing import Iterable, Any

from ..utils import IndexedView, reduce, FirepipeError


class Token:
  def __init__(self, string: str, pos: int, ttype: AbstractTokenType):
    self.string = string
    self.pos = pos
    self.type = ttype

  def __repr__(self):
    return f"[{self.string} {self.pos}]"

  def __reduce__(self):
    return reduce(self, (self.string, self.pos, self.type))

class AbstractTokenType:
  def lex(self, iview: IndexedView) -> Token | None:
    raise NotImplementedError

  def prepare(self, token: Token) -> Any:
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self)

  def __str__(self):
    return f"TokenType({type(self).__name__})"

class LexerError(FirepipeError):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
