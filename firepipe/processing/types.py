from __future__ import annotations
from typing import Sequence

from ..lexing.types import Token
from ..typing import RuntimeTypeSelector
from ..utils import reduce, FirepipeError


class Node:
  def __init__(self, args: Sequence[Node | Token]=(), ops: Sequence[Operator]=()):
    self.args = tuple(args)
    self.ops = tuple(ops)

  def __str__(self):
    args = ", ".join(map(str, self.args))
    ops = ", ".join(map(str, self.ops))
    return f"Node<{args}>({ops})"

  def simplify(self) -> Node:
    if len(self.args) == 1 and not self.ops:
      if isinstance(self.args[0], Node):
        return self.args[0]
    return self

  def __reduce__(self):
    return reduce(self, (self.args, self.ops))

class Operator:
  def __init__(self, token: Token, argc: int, type_selector: RuntimeTypeSelector, method: str):
    self.token = token
    self.argc = argc
    self.type_selector = type_selector
    self.method = method

  def __str__(self):
    return f"{{{self.token}}}"

  def __reduce__(self):
    return reduce(self, (self.token, self.argc, self.type_selector, self.method))

class ProcessorError(FirepipeError):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
