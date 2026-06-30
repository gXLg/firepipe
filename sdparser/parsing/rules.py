from ..executing.node import Node, Operator
from ..lexing.types import AbstractTokenType
from ..utils import reduce, setstate
from .step import Request, Result, Failure


class AbstractRule:
  def __init__(self, *rules):
    adapted_rules = []
    for rule in rules:
      if isinstance(rule, AbstractTokenType):
        rule = TokenRule(rule)
      elif isinstance(rule, str):
        rule = RefRule(rule)

      adapted_rules.append(rule)
    self.list = adapted_rules

  def process(self, iview, rules, state):
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self, ((),), ("list",))

  def __setstate__(self, state):
    return setstate(self, state)

  def __str__(self):
    return f"[{', '.join(map(str, self.list))}]"

class RefRule(AbstractRule):
  def __init__(self, key):
    super().__init__()
    self.key = key

  def process(self, iview, rules, state):
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

class Ordered(AbstractRule):
  def __init__(self, *rules):
    super().__init__(*rules)

  def process(self, iview, rules, state):
    if state and isinstance(state[-1], Failure):
      iview.restore()
      return Failure()
    if len(state) == len(self.list):
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
      iview.discard()
      return Result(Node(args, ops).simplify())
    if not state:
      iview.save()
    l = len(state)
    return Request(self.list[l])

class TokenRule(AbstractRule):
  def __init__(self, ttype):
    super().__init__()
    self.type = ttype

  def process(self, iview, rules, state):
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

class Or(AbstractRule):
  def __init__(self, *rules):
    super().__init__(*rules)

  def process(self, iview, rules, state):
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
  def __init__(self, *rules):
    super().__init__(*rules)

  def process(self, iview, rules, state):
    l = len(state) % len(self.list)
    if state and isinstance(state[-1], Failure):
      iview.restore()
      args = []
      ops = []
      for _res in state[:-l]:
        res = _res.result
        if isinstance(res, StarNode):
          args.extend(res.args)
          ops.extend(res.ops)
        elif isinstance(res, Node):
          args.append(res)
        elif isinstance(res, Operator):
          ops.append(res)
      return Result(Node(args, ops).simplify())
    if not l:
      if state:
        iview.discard()
      iview.save()
    return Request(self.list[l])

  def __str__(self):
    return f"[{', '.join(map(str, self.list))}]*"

class Star(Repeat):
  def __init__(self, *rules):
    super().__init__(*rules)

  def process(self, iview, rules, state):
    res = super().process(iview, rules, state)
    if isinstance(res, Result):
      node = res.result
      res = Result(StarNode(node.args, node.ops))
    return res

  def __str__(self):
    return f"*[{', '.join(map(str, self.list))}]*"

class Op(AbstractRule):
  def __init__(self, rule, argc, type_selector, method):
    super().__init__(rule)
    self.rule = rule
    self.argc = argc
    self.type_selector = type_selector
    self.method = method

  def process(self, iview, rules, state):
    if not state:
      return Request(self.list[0])
    res = state[-1]
    if isinstance(res, Failure):
      return res
    if not isinstance(res.result, Node):
      raise Exception("Only normal nodes can be declared as operators")
    if len(res.result.args) != 1:
      raise Exception("Operators should have exactly one argument")
    return Result(Operator(res.result.args[0], self))

  def __reduce__(self):
    return reduce(self, (self.rule, self.argc, self.type_selector, self.method))

  def __str__(self):
    return f"<{self.rule}>"

class ArgOp(Op):
  def __init__(self, rule, type_selector, method):
    super().__init__(rule, 0, type_selector, method)

  def process(self, iview, rules, state):
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
  def __init__(self, rule):
    super().__init__(rule)
    self.rule = rule

  def process(self, iview, rules, state):
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

class StarNode:
  def __init__(self, args=[], ops=[]):
    self.args = args
    self.ops = ops

  def __reduce__(self):
    return reduce(self, (self.args, self.ops))
