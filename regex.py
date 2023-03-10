import reparser


class Regex:
    def __init__(self, needle):
        self.needle = needle
        self.state_machine = reparser.Parser(reparser.lexer(needle)).parse()
        self.partial_state_machine = reparser.Parser(
            reparser.lexer(f".*{needle}.*")
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
