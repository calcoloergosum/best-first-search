"""overly-simplified A* implementation using best first search"""
from typing import Iterator, List, Optional, Tuple
from functools import partial
import math
import operator

import networkx as nx

from best_first_search import best_first_search


def estimated_cost(xy: Tuple[int, int], end: Tuple[int, int]) -> float:
    """Heuristic function"""
    x, y = xy
    return 0.5 * math.sqrt((end[0] - x) ** 2 + (end[1] - y) ** 2)


def get_neighbor(xy: Tuple[int, int], graph: nx.Graph, end: Tuple[int, int]
) -> Iterator[Tuple[float, Tuple[int, int]]]:
    """Pre-sorted neighbor iterator from graph"""
    x, y = xy
    cost_previous = estimated_cost(xy, end)
    neighbors = [
        (data['weight'] + estimated_cost(_xy, end) - cost_previous, _xy)
        for _, _xy, data in graph.edges((x, y), data=True)
    ]
    neighbors.sort()
    yield from neighbors


def a_star(
    graph: nx.Graph,
    start: Tuple[int, int],
    end: Tuple[int, int],
    n_thread: int = 0,
) -> Optional[Tuple[float, int, Tuple[Tuple[int, int], ...]]]:
    """Find shortest path from `start` to `end`.

    Args:
        graph (nx.Graph): grid graph, with `weight` property is set on edges
        start: starting node
        end: ending node
        n_thread: number of threads to run

    Returns:
        float: cost of the found path
        Tuple[Tuple[int, int], ...]: list of nodes along the found path

        None when a solution is not found
    """
    def is_solution(n):
        return n == end

    # run solver
    solution_iterator = best_first_search(
        estimated_cost(start, end), start, partial(get_neighbor, graph=graph, end=end), is_solution,
        cost_add=operator.add,
        n_thread=n_thread,
    )
    try:
        return next(solution_iterator)
    except StopIteration:
        return None


def a_star_debug(
    graph: nx.Graph,
    start: Tuple[int, int],
    end: Tuple[int, int],
    n_thread: int = 0,
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:  # pragma: no cover
    """Same as a_star, but return list of edges in search order"""
    edges = []

    def is_solution(n: Tuple[int, int]) -> bool:
        return n == end

    def _get_neighbor(xy: Tuple[int, int]) -> Iterator[Tuple[float, Tuple[int, int]]]:
        for cost, _xy in get_neighbor(xy, graph, end):
            edges.append((xy, _xy))
            yield (cost, _xy)

    solution_iterator = best_first_search(
        estimated_cost(start, end), start, _get_neighbor, is_solution,
        cost_add=operator.add,
        n_thread=n_thread,
    )
    try:
        next(solution_iterator)
    except StopIteration:
        pass
    return edges
