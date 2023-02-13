from dataclasses import dataclass, field
import typing


@dataclass
class Node:
    transitions: dict[str, "Node"] = field(default_factory=dict)
    trivial_neigbours: list["Node"] = field(default_factory=list)
    wildcard_match: typing.Optional["Node"] = None

    def match(self, char: str) -> typing.Optional["Node"]:
        return self.wildcard_match or self.transitions.get(char)

    def connect_trivial(self, n: "Node"):
        self.trivial_neigbours.append(n)

    def connect_literal(self, char: str, n: "Node"):
        self.transitions[char] = n

    def connect_dot(self, n: "Node"):
        self.wildcard_match = n


@dataclass
class Automaton:
    start: Node = field(default_factory=Node)
    end: Node = field(default_factory=Node)

    def concat(self, other: "Automaton") -> "Automaton":
        self.end.connect_trivial(other.start)
        return Automaton(self.start, other.end)

    def choice(self, *others: "Automaton") -> "Automaton":
        start, end = Node(), Node()
        for o in others:
            start.connect_trivial(o.start)
            o.end.connect_trivial(end)
        return Automaton(start, end)

    def clojure(self) -> "Automaton":
        self.end.connect_trivial(self.start)
        self.start.connect_trivial(self.end)
        return self


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
