from ..utils import reduce


class Token:
  def __init__(self, string, pos, ttype):
    self.string = string
    self.pos = pos
    self.type = ttype

  def __repr__(self):
    return f"[{self.string} {self.pos}]"

  def prepare(self):
    return self.type.prepare(self)

  def __reduce__(self):
    return reduce(self, (self.string, self.pos, self.type))
