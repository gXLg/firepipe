from __future__ import annotations
from typing import Sequence, Any

from .types import Node, ProcessorError
from ..lexing.types import Token
from ..utils import reduce, setstate


class Value:
  def __init__(self, value: Any):
    self.value = value

  def __reduce__(self):
    return reduce(self, (self.value,))

class ProcessorFrame:
  def __init__(self, node: Node):
    self.node = node
    self.arg_index = 0
    self.op_index = 0
    self.values = []

  def args_done(self) -> bool:
    return self.arg_index == len(self.node.args)

  def process_arg(self, stack: list[ProcessorFrame]):
    arg = self.node.args[self.arg_index]
    self.arg_index += 1
    if isinstance(arg, Node):
      stack.append(ProcessorFrame(arg))
    elif isinstance(arg, Token):
      self.values.append(Value(arg.type.prepare(arg)))
    elif isinstance(arg, Value):
      self.values.append(arg)
    else:
      raise UnknownProcessorFrameArgument(arg)

  def ops_done(self) -> bool:
    return self.op_index == len(self.node.ops)

  def process_op(self, env: Any):
    op = self.node.ops[self.op_index]
    self.op_index += 1
    args = [v.value for v in self.values[:op.argc]]
    selected_type = op.type_selector.select(op.token, env, args)
    func = getattr(selected_type, op.method)
    val = func(op.token, env, *args)
    self.values[:op.argc] = [Value(val)]

  def finalize(self, stack: list[ProcessorFrame]):
    if len(self.values) != 1:
      raise ProcessorResultsLenError(len(self.values))
    res = self.values[0]
    if not isinstance(res, Value):
      raise ProcessorResultTypeError(res)
    stack.pop()
    if stack:
      stack[-1].values.append(res)
    return res.value

  def step(self, env: Any, stack: list[ProcessorFrame]) -> Any:
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

class Processor:
  def __init__(self, env: Any):
    self.env = env

  def process(self, frame: ProcessorFrame) -> Any:
    stack = [frame]
    res = None
    while stack:
      frame = stack[-1]
      res = frame.step(self.env, stack)
    return res

  def __reduce__(self):
    return reduce(self, (self.env,))

class UnknownProcessorFrameArgument(ProcessorError):
  def __init__(self, argument: Any):
    super().__init__(f"Unknown type of processor-frame argument: '{argument}' of type {type(argument).__name__}")

class ProcessorResultsLenError(ProcessorError):
  def __init__(self, values: int):
    super().__init__(f"Frame produced {values} values, expected 1")

class ProcessorResultTypeError(ProcessorError):
  def __init__(self, result: Any):
    super().__init__(f"Frame execution resulted in a non-value object '{result}' of type {type(result).__name__}")
