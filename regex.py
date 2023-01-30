from dataclasses import dataclass
import typing


class Node(typing.Protocol):
    def match(self, haystack: str, idx: int) -> bool:
        ...


class Empty:
    def match(self, haystack: str, idx: int) -> bool:
        return True


@dataclass
class Wildcard:
    success: typing.Optional[Node] = None

    def match(self, haystack: str, idx: int) -> bool:
        if idx >= len(haystack):
            return False
        if self.success is None:
            return True
        return self.success.match(haystack, idx + 1)


@dataclass
class Literal:
    char: str
    success: typing.Optional[Node] = None

    def match(self, haystack: str, idx: int) -> bool:
        if idx >= len(haystack):
            return False
        if haystack[idx] != self.char:
            return False
        if self.success is None:
            return True
        return self.success.match(haystack, idx + 1)


class Regex:
    def __init__(self, needle):
        self.needle = needle
        self.state_machine = self._builder(needle)

    def match(self, haystack):
        return any(
            self.state_machine.match(haystack, i) for i in range(len(haystack) + 1)
        )

    @staticmethod
    def _builder(needle: str) -> Node:
        if not needle:
            return Empty()

        if needle[0] == ".":
            start = Wildcard()
        else:
            start = Literal(needle[0])
        state: list[Node] = [start]
        for c in needle[1:]:
            if c == ".":
                state.append(Wildcard())
            else:
                state.append(Literal(c))
            state[-2].success = state[-1]
        return start
