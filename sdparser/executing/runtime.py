from ..utils import reduce
from ..parsing.rules import Op, ArgOp

class RuntimeType: pass

class RuntimeTypeSelector:
  def select(self, token, env, args):
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self)

class DefaultSelector(RuntimeTypeSelector):
  def __init__(self, default_type):
    super().__init__()
    self.type = default_type

  def select(self, token, env, args):
    return self.type

  def __reduce__(self):
    return reduce(self, (self.type,))

  def create_op(self, rule, argc, name):
    return Op(rule, argc, self, f"_op_{name}")

  def create_arg_op(self, rule, name):
    return ArgOp(rule, self, f"_arg_{name}")
