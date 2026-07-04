from __future__ import annotations
from typing import Sequence, Any

from ..utils import IndexedView, reduce, setstate, FirepipeError
from ..lexing.types import Token
from ..processing.types import Node
from .types import AbstractRule, Request, Result, Failure, ParseError


class ParseFrame:
  def __init__(self, rule: AbstractRule):
    self.rule = rule
    self.state = []

  def step(self, iview: IndexedView, rules: dict[str, AbstractRule], stack: Sequence[ParseFrame]) -> Result | Failure | None:
    res = self.rule.process(iview, rules, self.state)
    if isinstance(res, Request):
      stack.append(ParseFrame(res.rule))
    elif isinstance(res, Result) or isinstance(res, Failure):
      stack.pop()
      if stack:
        stack[-1].state.append(res)
      return res
    else:
      raise UnknownParseFrameResult(res)

    return None

  def __reduce__(self):
    return reduce(self, (self.rule,), ("state",))

  def __setstate__(self, state):
    return setstate(self, state)

class Parser:
  def __init__(self, rules: dict[str, AbstractRule]):
    self.rules = rules
    if not "$" in rules:
      raise LookupError("The entry rule '$' is not defined!")
    self.init = rules["$"]

  def parse(self, tokens: Sequence[Token], frame: ParseFrame) -> Node:
    iview = IndexedView(tokens)
    stack = [frame]
    res = Failure(None)
    while stack:
      frame = stack[-1]
      res = frame.step(iview, self.rules, stack)
    if res is None:
      raise ParseError("Parser stack emptied before producing a result")
    if isinstance(res, Failure):
      raise UnexpectedToken(res.instead, res.expected)
    if not iview.done():
      raise UnexpectedToken(iview.peek(1)[0], [])
    return res.result

  def __reduce__(self):
    return reduce(self, (self.rules,))

class UnexpectedToken(ParseError):
  def __init__(self, token: Token, expected: Sequence[AbstractTokenType]):
    tok_str = f"token '{token.string}' at {token.pos}" if token else "(end-of-file)"
    exp_str = f"any of {', '.join(map(str, expected))}" if expected else "(end-of-file)"
    super().__init__(f"Unexpected {tok_str}, expected {exp_str}")

class UnknownParseFrameResult(ParseError):
  def __init__(self, result: Any):
    super().__init__(f"Unknown type of parse-frame result: '{result}' of type {type(result).__name__}")
