from ..utils import reduce
from .rules import Ordered, Star, Or
from .types import RuleArg


class BinInfLeft(Ordered):
  def __init__(self, left: RuleArg, op: RuleArg, right: RuleArg | None=None):
    super().__init__(left, Star(op, right if right else left))
    self.left = left
    self.op = op
    self.right = right

  def __reduce__(self):
    return reduce(self, (self.left, self.op, self.right))

class BinInfRight(Or):
  def __init__(self, left: RuleArg, op: RuleArg, right: RuleArg | None=None):
    super().__init__(Ordered(left, op, self), right if right else left)
    self.left = left
    self.op = op
    self.right = right

  def __reduce__(self):
    return reduce(self, (self.left, self.op, self.right))

class UnPref(Ordered):
  def __init__(self, op: RuleArg, right: RuleArg):
    super().__init__(op, right)
    self.op = op
    self.right = right

  def __reduce__(self):
    return reduce(self, (self.op, self.right))
