"""Best first search with pre-sorted iterator"""
from typing import Callable, Dict, Iterator, Optional, Tuple
from enum import IntEnum

from .heap import Cost, LazyHeap, Node, SortedIterator


class Signal(IntEnum):
    """Human readable signal"""
    CONTINUE = 0
    SOLUTION_FOUND = 1
    HEAP_EXHAUSTED = 2


def best_first_search(
    initial_cost: Cost,
    initial_node: Node,
    get_sorted_neighbor_iterator: Callable[[Node], SortedIterator[Cost, Node]],
    is_solution: Callable[[Node], bool],
    cost_add: Callable[[Cost, Cost], Cost],
    memoize_bound: bool = True,
    n_thread: int = 0,
) -> Iterator[Tuple[Cost, Tuple[Node, ...]]]:
    """
    Best first search function, as a minimization problem.

    Args:
        initial_cost (Cost): cost to start with
        initial_node (Node): node to start with
        get_sorted_neighbor_iterator (Callable[[Node], SortedIterator[Cost, Node]]):
            iterator through neighbors in cost ascending order
        is_solution (Callable[[Node], bool]): termination condition
        memoize_bound (bool):
            Prune search by using known bound to reach the node.
            When state space is known to be a tree, set this to `False` to save some memory.
        n_thread (int):
            Number of python threads to be used.
            It can be useful if `sorted_iterator` involves heavy external function call.
            When given 0, runs in main thread.

    Yields:
        Iterator[Tuple[Cost, Node]]: found solutions
    """
    if memoize_bound:
        node2known_cost: Dict[Node, Optional[Cost]] = {}
    heap: LazyHeap[Cost, Tuple[Node, ...]] = LazyHeap.new(n_thread)
    heap.push(iter([(initial_cost, (initial_node,))]))

    def _iterate(cost: Cost, nodes: Tuple[Node, ...]) -> SortedIterator:
        for _cost, _node in get_sorted_neighbor_iterator(nodes[-1]):
            yield cost_add(cost, _cost), (*nodes, _node)

    while True:
        heapitem = heap.pop()
        # No more to search
        if heapitem is None:
            return
        cost, nodes = heapitem

        if memoize_bound:
            if (
                (cost_found := node2known_cost.get(nodes[-1], None)) is not None
                and cost_found <= cost
            ):
                # There was a better path to this node
                continue
            node2known_cost[nodes[-1]] = cost

        # if not solution, continue searching
        if not is_solution(nodes[-1]):
            heap.push(_iterate(cost, nodes))
            continue

        # solution found!
        yield (cost, nodes)
