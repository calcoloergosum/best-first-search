"""Best first search with pre-sorted iterator"""
from typing import Callable, Dict, Iterator, Optional, Tuple
import itertools

from .heap import Cost, LazyHeap, Node, SortedIterator


def best_first_search(
    initial_cost: Cost,
    initial_node: Node,
    get_sorted_neighbor_iterator: Callable[[Node], SortedIterator[Cost, Node]],
    is_solution: Callable[[Node], bool],
    cost_add: Callable[[Cost, Cost], Cost],
    memoize_bound: bool = True,
    n_max_iters: Optional[int] = None,
    n_thread: int = 0,
) -> Iterator[Tuple[Cost, int, Tuple[Node, ...]]]:
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
        Iterator[Tuple[Cost, int, Tuple[Node, ...]]]: cost, steps, solution
    """
    if memoize_bound:
        node2best_cost: Dict[Node, Optional[Cost]] = {}
    heap: LazyHeap[Cost, Tuple[Node, ...]] = LazyHeap.new(n_thread)
    heap.push(iter([(initial_cost, (initial_node,))]))

    def _iterate(cost: Cost, nodes: Tuple[Node, ...]) -> SortedIterator:
        for _cost, _node in get_sorted_neighbor_iterator(nodes[-1]):
            cost_total = cost_add(cost, _cost)
            if memoize_bound:
                if (
                    (best_cost := node2best_cost.get(_node, None)) is not None
                    and best_cost <= cost_total
                ):
                    # There was a better path to this node
                    continue
                node2best_cost[_node] = cost_total
            yield cost_total, (*nodes, _node)

    for n_iter in itertools.count():
        heapitem = heap.pop()

        # Too many iterations
        if n_max_iters is not None and n_iter >= n_max_iters:
            heap.stop()
            return

        # No more to search
        if heapitem is None:
            heap.stop()
            return
        cost, nodes = heapitem

        # if not solution, continue searching
        if not is_solution(nodes[-1]):
            heap.push(_iterate(cost, nodes))
            continue

        # solution found!
        yield (cost, n_iter, nodes)
