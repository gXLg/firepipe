from ..utils import IndexedView, reduce, setstate
from ..executing.node import Node
from .rules import AbstractRule
from .step import Request, Result, Failure


class ParseFrame:
  def __init__(self, rule):
    self.rule = rule
    self.state = []

  def process(self, iview, rules, stack):
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
  def __init__(self, rules):
    self.rules = rules
    if not "$" in rules:
      raise Exception("The entry rule '$' is not defined!")
    self.init = rules["$"]

  def parse(self, tokens, frame):
    iview = IndexedView(tokens)
    stack = [frame]
    res = Failure()
    while stack:
      frame = stack[-1]
      res = frame.process(iview, self.rules, stack)
    if isinstance(res, Failure):
      raise Exception("Failed to parse")
    if not iview.done():
      raise Exception("Not all tokens were consumed")
    return res.result

  def __reduce__(self):
    return reduce(self, (self.rules,))
