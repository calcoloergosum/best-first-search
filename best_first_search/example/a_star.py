"""overly-simplified A* implementation using best first search"""
from typing import Tuple
import operator

import networkx as nx

from best_first_search import best_first_search


def a_star(
    graph: nx.Graph, start: Tuple[int, int], end: Tuple[int, int]
) -> Tuple[float, Tuple[Tuple[int, int], ...]]:
    """Find shortest path from `start` to `end`.

    Args:
        graph (nx.Graph): grid graph, with `weight` property is set on edges

    Returns:
        float: cost of the found path
        Tuple[Tuple[int, int], ...]: list of nodes along the found path
    """
    # defining heuristic and cost
    def heuristic(cost_and_node):
        cost, node = cost_and_node
        return cost + abs(end[0] - node[0]) + abs(end[1] - node[1])

    def get_neighbor(n):
        neighbors = [(data['weight'], _n) for _, _n, data in graph.edges(n, data=True)]
        neighbors.sort(key=heuristic)
        for _cost, _node in neighbors:
            yield (_cost, _node)

    # defininig termination condition
    def is_solution(n):
        return n == end

    # run solver
    solution_iterator = best_first_search(
        0., start, get_neighbor, is_solution, cost_add=operator.add)
    return next(solution_iterator)
