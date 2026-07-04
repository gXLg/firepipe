from typing import Any

from ..utils import reduce, setstate


class Env:
  def __init__(self):
    self.content = {}

  def handle(self, res: Any):
    raise NotImplementedError

  def __reduce__(self):
    return reduce(self, (), ("content",))

  def __setstate__(self, state):
    setstate(self, state)
