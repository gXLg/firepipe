from typing import Sequence, Any

from ..lexing.lexer import Lexer
from ..lexing.types import AbstractTokenType
from ..parsing.parser import Parser, ParseFrame
from ..parsing.types import AbstractRule
from ..processing.processor import Processor, ProcessorFrame
from ..utils import reduce
from .env import Env


class Machine:
  def __init__(self, token_types: Sequence[AbstractTokenType], rules: dict[str, AbstractRule], env: Env):
    self.token_types = token_types
    self.rules = rules
    self.env = env

    self.lexer = Lexer(tokens)
    self.parser = Parser(rules)
    self.processor = Processor(env)

  def work(self, text):
    tokens = self.lexer.lex(text)
    pframe = ParseFrame(self.parser.init)
    node = self.parser.parse(tokens, pframe)
    rframe = ProcessorFrame(node)
    result = self.processor.process(rframe)
    self.env.handle(result)
    return result

  def __reduce__(self):
    return reduce(self, (self.token_types, self.rules, self.env))
