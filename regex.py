import reparser
from optimizer import optimize_automaton


class Regex:
    def __init__(self, needle, **vars: "Regex"):
        self.needle = needle
        line_start = False
        line_end = False
        tokens = reparser.lexer(needle)
        if tokens and tokens[0].kind == reparser.TokenKind.Caret:
            tokens = tokens[1:]
            line_start = True
        if tokens and tokens[-1].kind == reparser.TokenKind.Dollar:
            tokens = tokens[:-1]
            line_end = True

        automaton_vars = {k: v.state_machine for k, v in vars.items()}
        self.state_machine = reparser.Parser(tokens, vars=automaton_vars).parse()

        # Partial match
        if not line_start:
            tokens = reparser.lexer(".*") + tokens
        if not line_end:
            tokens += reparser.lexer(".*")
        self.partial_state_machine = reparser.Parser(
            tokens, vars=automaton_vars
        ).parse()

        self.state_machine = optimize_automaton(self.state_machine)
        self.partial_state_machine = optimize_automaton(self.partial_state_machine)

    def full_match(self, haystack) -> bool:
        return self._match(haystack, self.state_machine)

    def match(self, haystack) -> bool:
        return self._match(haystack, self.partial_state_machine)

    def _match(self, haystack, state_machine) -> bool:
        nodes = {state_machine.start}
        for c in haystack:
            nodes = self._get_all_trivial(nodes)
            nodes = self._get_all_matches(nodes, c)
            if not nodes:
                # Will this be relevant, when we optimize the automaton/graph?
                return False
        nodes = self._get_all_trivial(nodes)
        return state_machine.end in nodes

    @staticmethod
    def _get_all_matches(nodes: set, c: str) -> set:
        new_nodes = set()
        for node in nodes:
            new_nodes.update(node.match(c))
        return new_nodes

    @staticmethod
    def _get_all_trivial(nodes: set) -> set:
        new_nodes = set(nodes)
        while new_nodes:
            new_new_nodes = set()
            for node in new_nodes:
                new_new_nodes.update(node.trivial_neigbours - nodes)
                nodes.update(node.trivial_neigbours)
            new_nodes = new_new_nodes
        return nodes
