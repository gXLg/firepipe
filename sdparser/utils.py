class IndexedView:
  def __init__(self, view, index=0):
    self.view = view
    self.index = index
    self.stack = []

  def step(self, n):
    self.index += n

  def peek(self, n):
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

def reduce(obj, constr=(), state=()):
  _state = {}
  for attr in state:
    if hasattr(obj, attr):
      _state[attr] = getattr(obj, attr)
  return (obj.__class__, tuple(constr), _state)

def setstate(obj, state):
  if state is None:
    return
  for attr in state:
    setattr(obj, attr, state[attr])
