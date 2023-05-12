from automaton import Automaton, Node


def optimize_automaton(auto: Automaton) -> Automaton:
    auto.start = optimize_node(auto.start)
    return auto


def optimize_node(node: Node) -> Node:
    if node.transitions or node.negative_match:
        return node
    edges = list(find_edges(node, set()))
    if len(edges) == 1:
        return edges[0]
    new_node = Node()
    for edge in edges:
        for char, nodes in edge.transitions.items():
            new_node.transitions[char].update(nodes)
        new_node.trivial_neigbours.update(edge.trivial_neigbours)
        new_node.negative_match.extend(edge.negative_match)
    return new_node


def find_edges(node: Node, visited: set[Node]) -> set[Node]:
    if node in visited:
        return set()
    visited.add(node)
    if node.transitions or node.negative_match:
        return {node}
    result = set()
    for n in node.trivial_neigbours:
        result.update(find_edges(n, visited))
    return result
