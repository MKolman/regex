import typing
import string
from dataclasses import dataclass, field
from enum import IntEnum, auto

from automaton import Automaton, Node


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
    Caret = auto()
    Dollar = auto()
    Digit = auto()
    Word = auto()
    Whitespace = auto()


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
            case "^":
                result.append(Token(TokenKind.Caret))
            case "$":
                result.append(Token(TokenKind.Dollar))
            case "\\":
                i += 1
                if i == len(code):
                    raise ValueError("Regex cannot end with a single backslash")
                match code[i]:
                    case "d":
                        result.append(Token(TokenKind.Digit))
                    case "w":
                        result.append(Token(TokenKind.Word))
                    case "s":
                        result.append(Token(TokenKind.Whitespace))
                    case _:
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
     - Grouping ()
     - Digit: \d = [0123456789]
     - Word: \w = [a-zA-Z0-9_]
     - Whitespace: \s = [ \t\n\r\f]
     - Bracket [abc] = (a|b|c)
     - Variable {a} = insert variable a
     - Range A{3} = AAA
     - Range A{1,3} = A(|A(|A))
     - OneOrMore: A+ = AA*
     - Optional: A? = (A|)
     - Clojure A* = (|A|AA|AAA|...)
     - Concatination AB
     - Choice (A|B)
    """

    tokens: list[Token]
    idx: int = 0
    vars: dict[str, Automaton] = field(default_factory=dict)

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
        while self.next() in [
            TokenKind.Literal,
            TokenKind.OpenParen,
            TokenKind.Dot,
            TokenKind.OpenBracket,
            TokenKind.OpenBrace,
            TokenKind.Digit,
            TokenKind.Word,
            TokenKind.Whitespace,
        ]:
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
        left = self.parse_range()
        if self.consume(TokenKind.Plus):
            left = left.concat(left.clone().clojure())
        return left

    def parse_range(self) -> Automaton:
        left = self.parse_variable()
        if self.consume(TokenKind.OpenBrace):
            # Don't parse variables here
            if self.next() != TokenKind.Literal or not self.next_value().isdigit():
                self.idx -= 1
                return left
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

    def parse_variable(self) -> Automaton:
        if self.consume(TokenKind.OpenBrace):
            assert (
                self.next() == TokenKind.Literal
            ), "Variable names must start with a letter"
            assert (
                self.next_value().isalpha()
            ), "Variable names must start with a letter"

            name = ""

            while c := self.consume_literal():
                assert (
                    c.isalnum() or c == "_"
                ), f"Variable names can only contain letters, numbers and underscores and not '{c}'."
                name += c

            assert self.consume(
                TokenKind.CloseBrace
            ), f"Variables cannot contain {self.next_value()}"

            assert name in self.vars, f"Variable {name} is not defined"

            return self.vars[name].clone()

        return self.parse_bracket()

    def parse_bracket(self) -> Automaton:
        if self.consume(TokenKind.OpenBracket):
            is_negative = self.consume(TokenKind.Caret)
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
            if is_negative:
                result.end = Node()
                result.start.connect_dot(result.end)
            return result
        return self.parse_whitespace()

    def parse_whitespace(self) -> Automaton:
        if self.consume(TokenKind.Whitespace):
            result = Automaton.none()
            for c in " \t\r\n\f":
                result.start.connect_literal(c, result.end)
            return result
        return self.parse_word()

    def parse_word(self) -> Automaton:
        if self.consume(TokenKind.Word):
            result = Automaton.none()
            for c in string.digits + string.ascii_letters + "_":
                result.start.connect_literal(c, result.end)
            return result
        return self.parse_digit()

    def parse_digit(self) -> Automaton:
        if self.consume(TokenKind.Digit):
            result = Automaton.none()
            for c in string.digits:
                result.start.connect_literal(c, result.end)
            return result
        return self.parse_group()

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
        return Automaton.empty()

    def next(self) -> TokenKind | None:
        return self.tokens[self.idx].kind if self.idx < len(self.tokens) else None

    def next_value(self) -> str | None:
        return self.tokens[self.idx].value if self.idx < len(self.tokens) else None

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
