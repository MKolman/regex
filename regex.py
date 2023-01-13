from dataclasses import dataclass, field
import typing


@dataclass
class Literal:
    jumps: dict[str, 'Literal'] = field(default_factory=dict)
    is_final: bool = False

    def match(self, haystack: str, idx: int, fallback: typing.Optional['Literal'] = None) -> bool:
        if self.is_final:
            return True
        if idx >= len(haystack):
            return False
        fallback = fallback or self
        return self.jumps.get(haystack[idx], fallback).match(haystack, idx + 1, fallback)

    @staticmethod
    def builder(needle: str) -> 'Literal':
        cur = Literal({}, True)
        for c in reversed(needle):
            cur = Literal({c: cur})
        return cur

def self_similar(s:str, i:int) -> int:
    """
    n = self_similar(s, i)
    s[i-n:i] == s[:n]
    """
    pass

class Regex:
    def __init__(self, needle):
        self.needle = needle
        self.state_machine = Literal.builder(needle)

    def match(self, haystack):
        return self.state_machine.match(haystack, 0)
