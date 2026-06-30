from __future__ import annotations
from typing import Iterable, Any

from .types import Node
from ..lexing.types import Token
from ..utils import reduce, setstate


class Value:
  def __init__(self, value: Any):
    self.value = value

  def __reduce__(self):
    return reduce(self, (self.value,))

class RunFrame:
  def __init__(self, node: Node):
    self.node = node
    self.arg_index = 0
    self.op_index = 0
    self.values = []

  def args_done(self) -> bool:
    return self.arg_index == len(self.node.args)

  def process_arg(self, stack: Iterable[RunFrame]):
    arg = self.node.args[self.arg_index]
    self.arg_index += 1
    if isinstance(arg, Node):
      stack.append(RunFrame(arg))
    elif isinstance(arg, Token):
      self.values.append(Value(arg.type.prepare(arg)))
    elif isinstance(arg, Value):
      self.values.append(arg)
    else:
      raise Exception("Unknown type of frame argument")

  def ops_done(self) -> bool:
    return self.op_index == len(self.node.ops)

  def process_op(self, env: Any):
    op = self.node.ops[self.op_index]
    self.op_index += 1
    args = [v.value for v in self.values[:op.argc]]
    selected_type = op.type_selector.select(op.token, env, args)
    func = getattr(selected_type, op.method)
    self.values[:op.argc] = [Value(func(op.token, env, *args))]

  def finalize(self, stack: Iterable[RunFrame]):
    if len(self.values) != 1:
      raise Exception(f"Frame produced {len(self.values)} values (instead of 1)")
    res = self.values[0]
    if not isinstance(res, Value):
      raise Exception(f"Frame execution resulted in a non-value object")
    stack.pop()
    if stack:
      stack[-1].values.append(res)
    return res.value

  def step(self, env: Any, stack: Iterable[RunFrame]) -> Any:
    if not self.args_done():
      self.process_arg(stack)
      return
    if not self.ops_done():
      self.process_op(env)
      return
    return self.finalize(stack)

  def __reduce__(self):
    return reduce(self, (self.node,), ("arg_index", "op_index", "values"))

  def __setstate__(self, state):
    setstate(self, state)

class Runner:
  def __init__(self, env: Any):
    self.env = env

  def run(self, frame: RunFrame) -> Any:
    stack = [frame]
    res = None
    while stack:
      frame = stack[-1]
      res = frame.step(self.env, stack)
    return res

  def __reduce__(self):
    return reduce(self, (self.env,))
