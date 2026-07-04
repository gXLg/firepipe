from typing import Sequence, Any


class IndexedView:
  def __init__(self, view: Sequence[Any], index: int=0):
    self.view = view
    self.index = index
    self.stack = []

  def step(self, n: int) -> Sequence[Any]:
    self.index += n

  def peek(self, n: int) -> Sequence[Any]:
    return self.view[self.index:self.index + n]

  def save(self):
    self.stack.append(self.index)

  def restore(self):
    self.index = self.stack.pop()

  def discard(self):
    self.stack.pop()

  def done(self):
    return self.index == len(self.view)

  def __reduce__(self):
    return reduce(self, (self.view, self.index), ("stack",))

  def __setstate__(self, state):
    setstate(self, state)

def reduce(obj: Any, constr: Sequence[Any]=(), state: Sequence[str]=()) -> tuple[type, tuple[Any], dict[str, Any]]:
  _state = {}
  for attr in state:
    if hasattr(obj, attr):
      _state[attr] = getattr(obj, attr)
  return (obj.__class__, tuple(constr), _state)

def setstate(obj: Any, state: dict[str, Any]):
  if state is None:
    return
  for attr in state:
    setattr(obj, attr, state[attr])

class FirepipeError(Exception):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
