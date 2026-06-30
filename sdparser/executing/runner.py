from .node import Node
from ..lexing.token import Token
from ..utils import reduce, setstate


class Value:
  def __init__(self, value):
    self.value = value

  def __reduce__(self):
    return reduce(self, (self.value,))

class Frame:
  def __init__(self, node):
    self.node = node
    self.arg_index = 0
    self.op_index = 0
    self.values = []

  def args_done(self):
    return self.arg_index == len(self.node.args)

  def process_arg(self, stack):
    arg = self.node.args[self.arg_index]
    self.arg_index += 1
    if isinstance(arg, Node):
      stack.append(Frame(arg))
    elif isinstance(arg, Token):
      self.values.append(Value(arg.prepare()))
    elif isinstance(arg, Value):
      self.values.append(arg)
    else:
      raise Exception("Unknown type of frame argument")

  def ops_done(self):
    return self.op_index == len(self.node.ops)

  def process_op(self, env):
    op = self.node.ops[self.op_index]
    self.op_index += 1
    args = [v.value for v in self.values[:op.argc]]
    selected_type = op.type_selector.select(op.token, env, args)
    func = getattr(selected_type, op.method)
    self.values[:op.argc] = [Value(func(op.token, env, *args))]

  def finalize(self, stack):
    if len(self.values) != 1:
      raise Exception(f"Frame produced {len(self.values)} values (instead of 1)")
    res = self.values[0]
    if not isinstance(res, Value):
      raise Exception(f"Frame execution resulted in a non-value object")
    stack.pop()
    if stack:
      stack[-1].values.append(res)
    return res.value

  def __reduce__(self):
    return reduce(self, (self.node,), ("arg_index", "op_index", "values"))

  def __setstate__(self, state):
    setstate(self, state)

class Runner:
  def __init__(self, env):
    self.env = env

  def run(self, frame):
    stack = [frame]
    res = None
    while stack:
      frame = stack[-1]
      if not frame.args_done():
        frame.process_arg(stack)
        continue
      if not frame.ops_done():
        frame.process_op(self.env)
        continue
      res = frame.finalize(stack)
    return res

  def __reduce__(self):
    return reduce(self, (self.env,))
