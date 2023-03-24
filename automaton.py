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

    def match(self, char: str) -> typing.Optional["Node"]:
        return self.transitions.get(char) or self.wildcard_match

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
    def none() -> "Automaton":
        return Automaton()

    @staticmethod
    def empty() -> "Automaton":
        result = Automaton()
        result.end = result.start
        return result

    @staticmethod
    def literal(lit: str) -> "Automaton":
        result = Automaton()
        result.start.connect_literal(lit, result.end)
        return result

    def clone(self) -> "Automaton":
        clone_lib = dict()
        self.start.rebuild(clone_lib)
        new_start = clone_lib[self.start._id]
        new_end = clone_lib[self.end._id]
        self.start.reconnect(clone_lib, set())
        return Automaton(new_start, new_end)

    def clone(self) -> "Automaton":
        new_start = Node()
        old_to_new = {self.start: new_start}  # Copied equivalent of the old node
        front = {self.start}
        while front:
            current_node = front.pop()
            current_new = old_to_new[current_node]
            for literal, node in current_node.transitions.items():
                # Make transitions equivalent to old ones
                if node not in old_to_new:
                    front.add(node)
                    old_to_new[node] = Node()
                current_new.transitions[literal] = old_to_new[node]
            for node in current_node.trivial_neigbours:
                # Match trivial neighbours equivalent to old ones
                if node not in old_to_new:
                    front.add(node)
                    old_to_new[node] = Node()
                current_new.trivial_neigbours.append(old_to_new[node])
            if current_node.wildcard_match:
                if current_node.wildcard_match not in old_to_new:
                    front.add(current_node.wildcard_match)
                    old_to_new[current_node.wildcard_match] = Node()
                current_new.wildcard_match = old_to_new[current_node.wildcard_match]
        return Automaton(new_start, old_to_new[self.end])

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
