import reparser


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

    def full_match(self, haystack) -> bool:
        return self._match(haystack, self.state_machine)

    def match(self, haystack) -> bool:
        return self._match(haystack, self.partial_state_machine)

    def _match(self, haystack, state_machine) -> bool:
        nodes = {state_machine.start}
        for c in haystack:
            nodes = self._get_all_trivial(nodes)
            nodes = {nei for node in nodes if (nei := node.match(c))}
            if not nodes:
                # Will this be relevant, when we optimize the automaton/graph?
                return False
        nodes = self._get_all_trivial(nodes)
        return state_machine.end in nodes

    def _get_all_trivial(self, nodes: set) -> set:
        new_nodes = set(nodes)
        while new_nodes:
            new_new_nodes = set()
            for node in new_nodes:
                for nei in node.trivial_neigbours:
                    if nei not in nodes:
                        nodes.add(nei)
                        new_new_nodes.add(nei)
            new_nodes = new_new_nodes
        return nodes
