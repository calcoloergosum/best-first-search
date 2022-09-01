"""Best first search with pre-sorted iterator"""
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Protocol, Tuple, TypeVar
from heapq import heappop, heappush

Node = TypeVar("Node")
Cost = TypeVar("Cost", bound="SupportsComparison")


class SupportsComparison(Protocol):
    """Comparable protocol"""
    def __eq__(self, other: Any) -> bool: ...
    def __lt__(self: Cost, other: Cost) -> bool: ...
    def __gt__(self: Cost, other: Cost) -> bool: ...
    def __le__(self: Cost, other: Cost) -> bool: ...
    def __ge__(self: Cost, other: Cost) -> bool: ...


SortedIterator = Iterator[Tuple[Cost, Node]]

class LazyHeap(Generic[Cost, Node]):
    """
    Lazily evaluated min-heap that pertains sorted iterators instead of actual items.
    """
    def __init__(self) -> None:
        self.heap: List[Tuple[Cost, int, Node, SortedIterator[Cost, Node]]] = []
        self._index: int = 0  # in case of the same cost, force FIFO

    def push(self, sorted_iterator: SortedIterator[Cost, Node]) -> None:
        """Push items to this heap"""
        try:
            cost, item = next(sorted_iterator)
            heappush(self.heap, (cost, self._index, item, sorted_iterator))
            self._index += 1
        except StopIteration:
            pass

    def pop(self) -> Optional[Tuple[Cost, Node]]:
        """Pop the minimum cost item from this heap"""
        while self.heap:
            cost, _, node, rest = heappop(self.heap)
            try:
                cost_next, node_next = next(rest)
                heappush(self.heap, (cost_next, self._index, node_next, rest))
                self._index += 1
            except StopIteration:
                pass
            return (cost, node)
        return None


def best_first_search(
    initial_cost: Cost,
    initial_node: Node,
    get_sorted_neighbor_iterator: Callable[[Node], SortedIterator[Cost, Node]],
    is_solution: Callable[[Node], bool],
    cost_add: Callable[[Cost, Cost], Cost],
    memoize_bound: bool = True,
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

    Yields:
        Iterator[Tuple[Cost, Node]]: found solutions
    """
    if memoize_bound:
        node2known_cost: Dict[Node, Optional[Cost]] = {}
    heap: LazyHeap[Cost, Tuple[Node, ...]] = LazyHeap()
    heap.push(iter([(initial_cost, (initial_node,))]))

    def _iterate(cost: Cost, nodes: Tuple[Node, ...]) -> SortedIterator:
        for _cost, _node in get_sorted_neighbor_iterator(nodes[-1]):
            yield cost_add(cost, _cost), (*nodes, _node)

    while result := heap.pop():
        # No more to search
        if result is None:
            return
        cost, nodes = result

        if memoize_bound:
            if (
                (cost_found := node2known_cost.get(nodes[-1], None)) is not None
                and cost_found <= cost
            ):
                continue
            node2known_cost[nodes[-1]] = cost

        # if not solution, continue searching
        if not is_solution(nodes[-1]):
            heap.push(_iterate(cost, nodes))
            continue

        # solution found!
        yield cost, nodes
    return


if __name__ == '__main__':
    import doctest
    doctest.testmod()
