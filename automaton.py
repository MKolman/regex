from dataclasses import dataclass, field
import typing

last_id = 0


def get_id() -> int:
    global last_id
    last_id += 1
    return last_id


@dataclass
class Node:
    transitions: dict[str, "Node"] = field(default_factory=dict)
    trivial_neigbours: list["Node"] = field(default_factory=list)
    wildcard_match: typing.Optional["Node"] = None
    _id: int = field(default_factory=get_id)

    def clone(self) -> "Node":
        return Node(
            self.transitions.copy(),
            self.trivial_neigbours.copy(),
            self.wildcard_match,
        )

    def match(self, char: str) -> typing.Optional["Node"]:
        return self.wildcard_match or self.transitions.get(char)

    def connect_trivial(self, n: "Node"):
        self.trivial_neigbours.append(n)

    def connect_literal(self, char: str, n: "Node"):
        self.transitions[char] = n

    def connect_dot(self, n: "Node"):
        self.wildcard_match = n

    def __hash__(self) -> int:
        return self._id

    def __eq__(self, o: "Node") -> bool:
        return self._id == o._id


@dataclass
class Automaton:
    start: Node = field(default_factory=Node)
    end: Node = field(default_factory=Node)

    @staticmethod
    def empty() -> "Automaton":
        result = Automaton()
        result.end = result.start
        return result

    def clone(self) -> "Automaton":
        return Automaton(self.start.clone(), self.end.clone())

    def concat(self, other: "Automaton") -> "Automaton":
        self.end.connect_trivial(other.start)
        return Automaton(self.start, other.end)

    def choice(self, *others: "Automaton") -> "Automaton":
        start, end = Node(), Node()
        start.connect_trivial(self.start)
        self.end.connect_trivial(end)
        for o in others:
            start.connect_trivial(o.start)
            o.end.connect_trivial(end)
        return Automaton(start, end)

    def clojure(self) -> "Automaton":
        self.end.connect_trivial(self.start)
        self.start.connect_trivial(self.end)
        return self
