from typing import Iterable, Any

from ..runtime.types import Node, Operator
from ..typing import RuntimeTypeSelector
from ..lexing.types import AbstractTokenType
from ..utils import IndexedView, reduce, setstate
from .types import AbstractRule, StarNode, Result, Request, Failure


def fill_node(state: Iterable[Result]):
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

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    if state and isinstance(state[-1], Failure):
      iview.restore()
      return Failure()
    if len(state) == len(self.list):
      iview.discard()
      return Result(fill_node(state))
    if not state:
      iview.save()
    l = len(state)
    return Request(self.list[l])

class Or(AbstractRule):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    if state and isinstance(state[-1], Failure):
      iview.restore()
    if state and isinstance(state[-1], Result):
      iview.discard()
      res = state[-1]
      if isinstance(res.result, Node):
        res = Result(res.result.simplify())
      return res
    if len(state) == len(self.list):
      return Failure()
    l = len(state)
    iview.save()
    return Request(self.list[l])

  def __str__(self):
    return f"[{' | '.join(f'({r})' for r in map(str, self.list))}]"

class Repeat(AbstractRule):
  def __init__(self, *rules: AbstractRule):
    super().__init__(*rules)

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result:
    l = len(state) % len(self.list)
    if state and isinstance(state[-1], Failure):
      iview.restore()
      cutoff = l if l else len(self.list)
      return Result(fill_node(state[:-cutoff]))
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

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result:
    res = super().process(iview, rules, state)
    if isinstance(res, Result):
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

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    if not state:
      return Request(self.list[0])
    res = state[-1]
    if isinstance(res, Failure):
      return res
    if not isinstance(res.result, Node):
      raise Exception("Only normal nodes can be declared as operators")
    if len(res.result.args) != 1:
      raise Exception("Operators should have exactly one argument")
    return Result(Operator(res.result.args[0], self.argc, self.method, self.type_selector))

  def __reduce__(self):
    return reduce(self, (self.rule, self.argc, self.type_selector, self.method))

  def __str__(self):
    return f"<{self.rule}>"

class ArgOp(Op):
  def __init__(self, rule: AbstractRule, type_selector: RuntimeTypeSelector, method: str):
    super().__init__(rule, 0, type_selector, method)

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
    res = super().process(iview, rules, state)
    if isinstance(res, Result):
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

  def process(self, iview: IndexedView, rules: dict[str, AbstractRule], state: Iterable[Result | Failure]) -> Request | Result | Failure:
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

