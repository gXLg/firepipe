from __future__ import annotations
from typing import Iterable, Any

from ..utils import IndexedView, reduce, setstate
from ..lexing.types import Token
from ..runtime.types import Node
from .types import AbstractRule, Request, Result, Failure


class ParseFrame:
  def __init__(self, rule: AbstractRule):
    self.rule = rule
    self.state = []

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], stack: Iterable[ParseFrame]) -> Result | Failure | None:
    res = self.rule.process(iview, rules, self.state)
    if isinstance(res, Request):
      stack.append(ParseFrame(res.rule))
    elif isinstance(res, Result) or isinstance(res, Failure):
      stack.pop()
      if stack:
        stack[-1].state.append(res)
      return res
    else:
      raise Exception("Unknown type of parser frame result")

  def __reduce__(self):
    return reduce(self, (self.rule,), ("state",))

  def __setstate__(self, state):
    return setstate(self, state)

class Parser:
  def __init__(self, rules: dict[str, AbstractRule]):
    self.rules = rules
    if not "$" in rules:
      raise Exception("The entry rule '$' is not defined!")
    self.init = rules["$"]

  def parse(self, tokens: Iterable[Token], frame: ParseFrame) -> Node:
    iview = IndexedView(tokens)
    stack = [frame]
    res = Failure()
    while stack:
      frame = stack[-1]
      res = frame.process(iview, self.rules, stack)
    if res is None or isinstance(res, Failure):
      raise Exception("Failed to parse")
    if not iview.done():
      raise Exception("Not all tokens were consumed")
    return res.result

  def __reduce__(self):
    return reduce(self, (self.rules,))
