from typing import Sequence, Any, cast

from ..processing.types import Node, Operator
from ..typing import RuntimeTypeSelector
from ..lexing.types import Token, AbstractTokenType
from ..utils import IndexedView, reduce, setstate
from .types import (
  AbstractRule, StarNode, Result, Request, Failure, ParseError
)


def fill_node(state: Sequence[Result]):
  args = []
  ops = []
  for _res in state:
    res = _res.result
    if isinstance(res, StarNode):
      args.extend(res.args)
      ops.extend(res.ops)
    elif isinstance(res, Node):
      args.append(res)
    elif isinstance(res, Operator):
      ops.append(res)

  return Node(args, ops).simplify()

class Ordered(AbstractRule):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result | Failure:
    if state and isinstance(state[-1], Failure):
      iview.restore()
      return state[-1]
    if len(state) == len(self.list):
      iview.discard()
      return Result(fill_node(cast(Sequence[Result], state)))
    if not state:
      iview.save()
    l = len(state)
    return Request(self.list[l])

class Or(AbstractRule):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result | Failure:
    if state and isinstance(state[-1], Failure):
      iview.restore()
    if state and isinstance(state[-1], Result):
      iview.discard()
      res = state[-1]
      if isinstance(res.result, Node):
        res = Result(res.result.simplify())
      return res
    if len(state) == len(self.list):
      token = None if iview.done() else iview.peek(1)[0]
      # filter out the furthest failures
      last = token.pos if token else -1
      exp = set()
      for failure in cast(Sequence[Failure], state):
        if failure.instead is None:
          token = None
          last = float("inf")
          exp = {*failure.expected}
        elif failure.instead.pos > last:
          token = failure.instead
          last = token.pos
          exp = {*failure.expected}
        elif failure.instead.pos == last:
          exp.update(failure.expected)
      return Failure(token, *exp)
    l = len(state)
    iview.save()
    return Request(self.list[l])

  def __str__(self):
    return f"[{' | '.join(f'({r})' for r in map(str, self.list))}]"

class Repeat(AbstractRule):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result:
    l = len(state) % len(self.list)
    if state and isinstance(state[-1], Failure):
      iview.restore()
      cutoff = l if l else len(self.list)
      return Result(fill_node(cast(Sequence[Result], state[:-cutoff])))
    if not l:
      if state:
        iview.discard()
      iview.save()
    return Request(self.list[l])

  def __str__(self):
    return f"[{', '.join(map(str, self.list))}]*"

class Star(Repeat):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result:
    res = super().process(iview, rules, state)
    if isinstance(res, Result) and isinstance(res.result, Node):
      node = res.result
      res = Result(StarNode(node.args, node.ops))
    return res

  def __str__(self):
    return f"*[{', '.join(map(str, self.list))}]*"

class Op(AbstractRule):
  def __init__(self, rule: AbstractRule, argc: int, type_selector: RuntimeTypeSelector, method: str):
    super().__init__(rule)
    self.rule = rule
    self.argc = argc
    self.type_selector = type_selector
    self.method = method

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result | Failure:
    if not state:
      return Request(self.list[0])
    res = state[-1]
    if isinstance(res, Failure):
      return res
    if not isinstance(res.result, Node):
      raise NonNodeError(res.result)
    if len(res.result.args) != 1:
      raise BadArgsError(len(res.result.args))
    if not isinstance(res.result.args[0], Token):
      raise ArgsTokenError(res.result)
    return Result(Operator(res.result.args[0], self.argc, self.method, self.type_selector))

  def __reduce__(self):
    return reduce(self, (self.rule, self.argc, self.type_selector, self.method))

  def __str__(self):
    return f"<{self.rule}>"

class ArgOp(Op):
  def __init__(self, rule: AbstractRule, type_selector: RuntimeTypeSelector, method: str):
    super().__init__(rule, 0, type_selector, method)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result | Failure:
    res = super().process(iview, rules, state)
    if isinstance(res, Result) and isinstance(res.result, Operator):
      op = res.result
      res = Result(Node(ops=[op]))
    return res

  def __reduce__(self):
    return reduce(self, (self.rule, self.type_selector, self.method))

  def __str__(self):
    return f"<$ {self.rule}>"

class Syntax(AbstractRule):
  def __init__(self, rule: AbstractRule):
    super().__init__(rule)
    self.rule = rule

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result | Failure:
    if not state:
      return Request(self.list[0])
    res = state[-1]
    if isinstance(res, Failure):
      return res
    return Result(StarNode())

  def __reduce__(self):
    return reduce(self, (self.rule,))

  def __str__(self):
    return f"({self.rule})"

class Optional(Ordered):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView[Sequence[Token]], rules: dict[str, AbstractRule], state: Sequence[Result | Failure]) -> Request | Result:
    res = super().process(iview, rules, state)
    if isinstance(res, Failure):
      res = Result(StarNode())
    if isinstance(res, Result) and isinstance(res.result, Node):
      node = res.result
      res = Result(StarNode(node.args, node.ops))
    return res

class OperatorError(ParseError):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

class NonNodeError(OperatorError):
  def __init__(self, result: Any):
    super().__init__(f"Only normal nodes can be declared as operators, tried with '{result}' of type {type(result).__name__}")

class BadArgsError(OperatorError):
  def __init__(self, args: int):
    super().__init__(f"Operators should have exactly one argument, provided: {args}")

class ArgsTokenError(OperatorError):
  def __init__(self, result: Any):
    super().__init__(f"Operator argument should be a Token, tried with '{result}' of type {type(result).__name__}")
