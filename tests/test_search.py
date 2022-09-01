import networkx as nx
import pytest

from best_first_search.example import a_star


@pytest.mark.parametrize("size", range(20, 25))
def test_best_first_search_by_a_star(size: int) -> None:
    """
    Implement A* using `best_first_search`, and solve the problem illustrated in the following gif.

    https://upload.wikimedia.org/wikipedia/commons/8/85/Weighted_A_star_with_eps_5.gif

    Make 2D grid with 8-adjacency, but some blocks are missing in the middle.
    """
    # graph making
    graph = nx.grid_2d_graph(size + 1, size + 1)

    # make graph 8-adjacent
    graph.add_edges_from([
        ((x + 1, y), (x, y + 1))
        for x in range(size)
        for y in range(size)
    ])
    graph.add_edges_from([
        ((x, y), (x + 1, y + 1))
        for x in range(size)
        for y in range(size)
    ])

    # every edge has the same cost
    for edge in graph.edges:
        graph.edges[edge]['weight'] = 1

    # remove some nodes in the middle to block direct path
    for i in range(5, size - 3):
        graph.remove_node((size // 2, i))
        if i == size // 2:
            continue
        graph.remove_node((i, size // 2))

    cost, solution = a_star(graph, (0, 0), (size, size))
    assert cost == size + (size + 1) // 2 - 3, size + (size + 1) // 2 - 3
    assert len(solution) == 1 + cost
