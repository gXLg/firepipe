from __future__ import annotations
from typing import Iterable, Any

from ..processing.types import Node, Operator
from ..lexing.types import AbstractTokenType, Token
from ..utils import IndexedView, reduce

class AbstractRule:
  def __init__(self, *rules: AbstractRule):
    adapted_rules = []
    for rule in rules:
      if isinstance(rule, AbstractTokenType):
        rule = TokenRule(rule)
      elif isinstance(rule, str):
        rule = RefRule(rule)

      adapted_rules.append(rule)
    self.list = adapted_rules

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self, ((),), ("list",))

  def __setstate__(self, state):
    return setstate(self, state)

  def __str__(self):
    return f"[{', '.join(map(str, self.list))}]"

class RefRule(AbstractRule):
  def __init__(self, key: str):
    super().__init__()
    self.key = key

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    if not state:
      if self.key == "$":
        raise Exception("Referencing the entry rule")
      if self.key not in rules:
        raise Exception("Referencing non-existing rule")
      return Request(rules[self.key])

    res = state[0]
    if isinstance(res, Result):
      if isinstance(res.result, Node):
        res = Result(res.result.simplify())
    return res

  def __reduce__(self):
    return reduce(self, (self.key,))

  def __str__(self):
    return f"(->{self.key})"

class TokenRule(AbstractRule):
  def __init__(self, ttype: AbstractTokenType):
    super().__init__()
    self.type = ttype

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Result | Failure:
    if iview.done():
      return Failure()
    token = iview.peek(1)[0]
    if token.type != self.type:
      return Failure()
    iview.step(1)
    return Result(Node([token]))

  def __reduce__(self):
    return reduce(self, (self.type,))

  def __str__(self):
    return str(self.type)

class StarNode:
  def __init__(self, args: Iterable[Node | Token]=(), ops: Iterable[Operator]=()):
    self.args = args
    self.ops = ops

  def __reduce__(self):
    return reduce(self, (self.args, self.ops))

class Request:
  def __init__(self, rule: AbstractRule):
    self.rule = rule

  def __reduce__(self):
    return reduce(self, (self.rule,))

class Result:
  def __init__(self, result: Any):
    self.result = result

  def __reduce__(self):
    return reduce(self, (self.result,))

class Failure:
  def __reduce__(self):
    return reduce(self)
