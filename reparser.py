import typing
from dataclasses import dataclass
from enum import IntEnum, auto

from automaton import Automaton


class TokenKind(IntEnum):
    Literal = auto()
    OpenParen = auto()
    CloseParen = auto()
    Dot = auto()
    Star = auto()
    Pipe = auto()
    Questionmark = auto()
    Plus = auto()


@dataclass
class Token:
    kind: TokenKind
    value: typing.Optional[str] = None


def lexer(code: str) -> list[Token]:
    result = []
    i = 0
    while i < len(code):
        match code[i]:
            case "?":
                result.append(Token(TokenKind.Questionmark))
            case "+":
                result.append(Token(TokenKind.Plus))
            case "(":
                result.append(Token(TokenKind.OpenParen))
            case ")":
                result.append(Token(TokenKind.CloseParen))
            case ".":
                result.append(Token(TokenKind.Dot))
            case "*":
                result.append(Token(TokenKind.Star))
            case "|":
                result.append(Token(TokenKind.Pipe))
            case "\\":
                i += 1
                if i == len(code):
                    raise ValueError("Regex cannot end with a single backslash")
                result.append(Token(TokenKind.Literal, code[i]))
            case c:
                result.append(Token(TokenKind.Literal, c))
        i += 1
    return result


@dataclass
class Parser:
    """
    Precedence:
     - Literal
     - Grouping
     - OneOrMore: A+ = AA*
     - Optional: A? = (A|)
     - Clojure A* = (|A|AA|AAA|...)
     - Concatination AB
     - Choice (A|B)
    """

    tokens: list[Token]
    idx: int = 0

    def parse(self) -> Automaton:
        if not self.tokens:
            return Automaton.empty()

        result = self.parse_choice()
        assert self.idx == len(
            self.tokens
        ), f"Unable to parse regex: parsed {self.idx}/{len(self.tokens)} {self.tokens[:self.idx]} but not {self.tokens[self.idx:]}"
        return result

    def parse_choice(self) -> Automaton:
        """a|b|c|d|g|h|l"""
        left = self.parse_concat()
        choices = []
        while self.consume(TokenKind.Pipe):
            choices.append(self.parse_concat())
        if choices:
            left = left.choice(*choices)
        return left

    def parse_concat(self) -> Automaton:
        left = self.parse_clojure()
        while self.next() in [TokenKind.Literal, TokenKind.OpenParen, TokenKind.Dot]:
            left = left.concat(self.parse_clojure())
        return left

    def parse_clojure(self) -> Automaton:
        left = self.parse_optional()
        if self.consume(TokenKind.Star):
            left = left.clojure()
        return left

    def parse_optional(self) -> Automaton:
        left = self.parse_one_or_more()
        if self.consume(TokenKind.Questionmark):
            left = left.choice(Automaton.empty())
        return left

    def parse_one_or_more(self) -> Automaton:
        left = self.parse_group()
        if self.consume(TokenKind.Plus):
            left = left.concat(left.clone().clojure())
        return left

    def parse_group(self) -> Automaton:
        if self.consume(TokenKind.OpenParen):
            result = self.parse_choice()
            assert self.consume(TokenKind.CloseParen)
            return result
        return self.parse_literal()

    def parse_literal(self) -> Automaton:
        if self.next() not in [TokenKind.Literal, TokenKind.Dot]:
            return Automaton.empty()
        result = Automaton()
        if self.consume(TokenKind.Dot):
            result.start.connect_dot(result.end)
        else:
            result.start.connect_literal(self.tokens[self.idx].value, result.end)
            self.idx += 1
        return result

    def next(self) -> TokenKind | None:
        return self.tokens[self.idx].kind if self.idx < len(self.tokens) else None

    def consume(self, kind: TokenKind) -> bool:
        if self.next() == kind:
            self.idx += 1
            return True
        return False
