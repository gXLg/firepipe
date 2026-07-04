from typing import Sequence, Any

from ..lexing.lexer import Lexer
from ..lexing.types import Token
from ..parsing.parser import Parser, ParseFrame
from ..parsing.types import AbstractRule
from ..processing.processor import Processor, ProcessorFrame
from ..utils import reduce
from .env import Env


class Machine:
  def __init__(self, tokens: Sequence[Token], rules: dict[str, AbstractRule], env: Env):
    self.tokens = tokens
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
    return reduce(self, (self.tokens, self.rules, self.env))
