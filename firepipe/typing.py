from typing import Iterable, Any

from .lexing.types import Token
from .utils import reduce


class RuntimeType: pass

class RuntimeTypeSelector:
  def select(self, token: Token, env: Any, args: Iterable[Any]) -> RuntimeType:
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self)

class DefaultSelector(RuntimeTypeSelector):
  def __init__(self, default_type: RuntimeType):
    super().__init__()
    self.type = default_type

  def select(self, token: Token, env: Any, args: Iterable[Any]) -> RuntimeType:
    return self.type

  def __reduce__(self):
    return reduce(self, (self.type,))
