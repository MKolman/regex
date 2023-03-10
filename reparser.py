import typing
from dataclasses import dataclass
from enum import IntEnum, auto

from automaton import Automaton


class TokenKind(IntEnum):
    Literal = auto()
    OpenParen = auto()
    CloseParen = auto()
    OpenBrace = auto()
    CloseBrace = auto()
    OpenBracket = auto()
    CloseBracket = auto()
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
            case "{":
                result.append(Token(TokenKind.OpenBrace))
            case "}":
                result.append(Token(TokenKind.CloseBrace))
            case "[":
                result.append(Token(TokenKind.OpenBracket))
            case "]":
                result.append(Token(TokenKind.CloseBracket))
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
                result.append(Token(TokenKind.Literal))
            case _:
                result.append(Token(TokenKind.Literal))
        result[-1].value = code[i]
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
     - Bracket [abc] = (a|b|c)
     - Range A{3} = AAA
     - Range A{1,3} = A(|A(|A))
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
        left = self.parse_range()
        while self.next() in [
            TokenKind.Literal,
            TokenKind.OpenParen,
            TokenKind.Dot,
            TokenKind.OpenBracket,
        ]:
            left = left.concat(self.parse_range())
        return left

    def parse_range(self) -> Automaton:
        left = self.parse_bracket()
        if self.consume(TokenKind.OpenBrace):
            min = 0
            while (digit := self.consume_digit()) is not None:
                min = min * 10 + int(digit)
            max = min
            if self.consume_literal(","):
                max = 0
                while (digit := self.consume_digit()) is not None:
                    max = max * 10 + int(digit)

            assert self.consume(TokenKind.CloseBrace)
            assert min <= max
            orig = left
            left = Automaton.empty()
            for _ in range(min):
                left = left.concat(orig.clone())
            for _ in range(max - min):
                left = left.concat(Automaton.empty().choice(orig.clone()))
        return left

    def parse_bracket(self) -> Automaton:
        if self.consume(TokenKind.OpenBracket):
            lits = []
            while not self.consume(TokenKind.CloseBracket):
                lits.append(self.tokens[self.idx].value)
                self.idx += 1
            assert len(lits) > 0
            result = Automaton()
            for idx, lit in enumerate(lits):
                if lit == "-" and idx > 0 and idx < len(lits) - 1:
                    start = lits[idx - 1]
                    end = lits[idx + 1]
                    for i in range(ord(start), ord(end) + 1):
                        result.start.connect_literal(chr(i), result.end)
                else:
                    result.start.connect_literal(lit, result.end)
            return result
        return self.parse_clojure()

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
        if self.consume(TokenKind.Dot):
            result = Automaton()
            result.start.connect_dot(result.end)
            return result
        if lit := self.consume_literal():
            result = Automaton.literal(lit)
            return result
        assert "Invalid literal?"

    def next(self) -> TokenKind | None:
        return self.tokens[self.idx].kind if self.idx < len(self.tokens) else None

    def consume_digit(self) -> int | None:
        if self.next() == TokenKind.Literal and self.tokens[self.idx].value.isdigit():
            self.idx += 1
            return int(self.tokens[self.idx - 1].value)
        return None

    def consume_literal(self, lit: str | None = None) -> str | None:
        if self.next() == TokenKind.Literal and (
            lit is None or self.tokens[self.idx].value in lit
        ):
            self.idx += 1
            return self.tokens[self.idx - 1].value
        return None

    def consume(self, kind: TokenKind) -> bool:
        if self.next() == kind:
            self.idx += 1
            return True
        return False
