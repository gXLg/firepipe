from ..utils import reduce

class Node:
  def __init__(self, args=[], ops=[]):
    self.args = args
    self.ops = ops

  def __str__(self):
    args = ", ".join(map(str, self.args))
    ops = ", ".join(map(str, self.ops))
    return f"Node<{args}>({ops})"

  def simplify(self):
    if len(self.args) == 1 and not self.ops:
      if isinstance(self.args[0], Node):
        return self.args[0]
    return self

  def __reduce__(self):
    return reduce(self, (self.args, self.ops))

class Operator:
  def __init__(self, token, op):
    self.token = token
    self.op = op
    self.argc = op.argc
    self.method = op.method
    self.type_selector = op.type_selector

  def __str__(self):
    return f"{{{self.token}}}"

  def __reduce__(self):
    return reduce(self, (self.token, self.op))
