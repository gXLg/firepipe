from ..utils import reduce

class Request:
  def __init__(self, rule):
    self.rule = rule

  def __reduce__(self):
    return reduce(self, (self.rule,))

class Result:
  def __init__(self, result):
    self.result = result

  def __reduce__(self):
    return reduce(self, (self.result,))

class Failure:
  def __reduce__(self):
    return reduce(self)
