"""
Implement A* using `best_first_search`, and solve the problem illustrated in the following gif.

https://upload.wikimedia.org/wikipedia/commons/8/85/Weighted_A_star_with_eps_5.gif
"""
import networkx as nx
import pytest

from best_first_search.example import a_star, a_star_debug


def _grid_graph(size: int) -> nx.Graph:
    """
    Make 2D grid with 8-adjacency, but some blocks are missing in the middle.
    """
    assert size > 9

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
    for i in range(4, size - 3):
        graph.remove_node((size - 4, i))
    for j in range(6, size - 4):
        graph.remove_node((j, size - 4))
    return graph


def _impossible_graph(size: int) -> nx.Graph:
    """
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

    # Cut in the middle
    for i in range(0, size + 1):
        graph.remove_node((size // 2, i))
    assert not nx.is_connected(graph)
    return graph


@pytest.mark.parametrize("size", range(20, 21))
def test_singlethread(size: int) -> None:
    """Single threaded test"""
    graph = _grid_graph(size)
    cost, _, solution = a_star(graph, (0, 0), (size, size), n_thread=0)
    assert abs(2 * size - 9 - cost) < 1e-7
    assert len(solution) == 1 + round(cost)
    assert solution[-1] == (size, size)


@pytest.mark.parametrize("size", range(20, 21))
def test_multithread(size: int) -> None:
    """Multi threaded test"""
    graph = _grid_graph(size)
    cost, _, solution = a_star(graph, (0, 0), (size, size), n_thread=4)
    assert abs(2 * size - 9 - cost) < 1e-7
    assert len(solution) == 1 + round(cost)
    assert solution[-1] == (size, size)


@pytest.mark.parametrize("size", range(10, 11))
def test_singlethread_impossible(size: int) -> None:
    """Single threaded test"""
    assert a_star(_impossible_graph(size), (0, 0), (size, size), n_thread=0) is None


@pytest.mark.parametrize("size", range(10, 11))
def test_multithread_impossible(size: int) -> None:
    """Multi threaded test"""
    assert a_star(_impossible_graph(size), (0, 0), (size, size), n_thread=4) is None


@pytest.mark.visualize
@pytest.mark.parametrize("size", range(15, 16))
def test_visualize(size: int) -> None:
    """Visualization"""
    import inspect

    from matplotlib import collections as mc
    from matplotlib import pyplot as plt
    testname = inspect.currentframe().f_code.co_name
    graph = _grid_graph(size)
    edges = a_star_debug(graph, (0, 0), (size, size), n_thread=4)

    _edges = []
    _colors = []
    for i, e in enumerate(edges):
        _edges.append(e)
        _colors.append((1, 0, 0, 1))

        lc = mc.LineCollection(_edges, colors=_colors)
        fig, ax = plt.subplots()
        ax.add_collection(lc)
        ax.set_xlim(-1, size + 1)
        ax.set_ylim(-1, size + 1)
        ax.margins(0.1)
        fig.savefig(f"{testname}_{i:0>5}.png")
        _colors[-1] = ((0.3, 0.3, 0.3, 1))
