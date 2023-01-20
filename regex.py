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
    fail: typing.Optional[Node] = None
    success: typing.Optional[Node] = None

    def match(self, haystack: str, idx: int) -> bool:
        if idx >= len(haystack):
            return False
        if haystack[idx] == self.char:
            if self.success is None:
                return True
            return self.success.match(haystack, idx + 1)
        elif self.fail is not None:
            return self.fail.match(haystack, idx)
        else:
            return self.match(haystack, idx + 1)


def fail_table(needle: str) -> list[typing.Optional[int]]:
    """https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm#Description_of_pseudocode_for_the_table-building_algorithm"""
    pos = 1
    candidate = 0
    jump_table = [None] * len(needle)
    for pos, current in enumerate(needle[1:], 1):
        if current == needle[candidate]:
            jump_table[pos] = jump_table[candidate]
        else:
            jump_table[pos] = candidate
            while candidate is not None and current != needle[candidate]:
                candidate = jump_table[candidate]
        candidate = 0 if candidate is None else candidate + 1
    return jump_table


class Regex:
    def __init__(self, needle):
        self.needle = needle
        self.state_machine = self._builder(needle)

    def match(self, haystack):
        return self.state_machine.match(haystack, 0)

    @staticmethod
    def _builder(needle: str) -> Node:
        if not needle:
            return Empty()

        fail_idxs = fail_table(needle)
        if needle[0] == ".":
            start = Wildcard()
        else:
            start = Literal(needle[0])
        state: list[Node] = [start]
        for fail_idx, c in zip(fail_idxs[1:], needle[1:]):
            if c == ".":
                state.append(Wildcard())
            else:
                fail = start if fail_idx is None else state[fail_idx]
                state.append(Literal(c, fail))
            state[-2].success = state[-1]
        return start
