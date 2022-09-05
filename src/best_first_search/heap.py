"""
Lazily evaluated min-heap that pertains sorted iterators instead of actual items.
"""
from typing import Any, Deque, Generic, Iterator, List, Optional, Protocol, Tuple, Type, TypeVar, cast
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from heapq import heappop, heappush
from threading import Lock

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

_Self = TypeVar('_Self', bound='LazyHeap')

class LazyHeap(Generic[Cost, Node]):
    """Interface for heap implementations"""
    def push(self, sorted_iterator: SortedIterator[Cost, Node]) -> None:
        """Push items to this heap"""

    def pop(self) -> Optional[Tuple[Cost, Node]]:
        """Pop the minimum cost item from this heap"""

    @classmethod
    def new(cls: Type[_Self], n_thread: int = 0) -> _Self:
        """Factory to make lazy heap"""
        if n_thread <= 0:
            return cast(_Self, LazyHeapSingleThread())
        return cast(_Self, LazyHeapMultithread(n_thread))

    def stop(self) -> None:
        """Stop the jobs"""


class LazyHeapSingleThread(LazyHeap[Cost, Node]):
    """single thread lazy heap"""
    def __init__(self) -> None:
        self.heap: List[Tuple[Cost, int, Node, SortedIterator[Cost, Node]]] = []
        self.index: int = 0  # in case of the same cost, force FIFO

    def push(self, sorted_iterator: SortedIterator[Cost, Node]) -> None:
        """Push items to this heap"""
        try:
            cost, item = next(sorted_iterator)
            heappush(self.heap, (cost, self.index, item, sorted_iterator))
            self.index += 1
        except StopIteration:
            pass

    def stop(self) -> None:
        pass

    def pop(self) -> Optional[Tuple[Cost, Node]]:
        """Pop the minimum cost item from this heap"""
        while self.heap:
            cost, _, node, rest = heappop(self.heap)
            try:
                cost_next, node_next = next(rest)
                heappush(self.heap, (cost_next, self.index, node_next, rest))
                self.index += 1
            except StopIteration:
                pass
            return (cost, node)
        return None

    push.__doc__ = LazyHeap.push.__doc__
    pop.__doc__ = LazyHeap.pop.__doc__


class LazyHeapMultithread(LazyHeap[Cost, Node]):
    """
    Multithreaded lazy heap. Not thread-safe.

    Execution Model:

    External pusher          External processor
    |                             ^
    |                             |
    V                             |
    Pushing ----> Container -----> Popping
    ^                             |
    |                             |
    +------Internal Iterator------+

    1. Popper: When others pushing, wait then pop
    2. Pusher: When others pushing, wait then push
               When others popping, push then release
    """
    def __init__(self, n_thread: int) -> None:
        assert n_thread > 0
        self.heap: List[Tuple[Cost, int, Node, SortedIterator[Cost, Node]]] = []
        self.index: int = 0  # in case of the same cost, force FIFO
        self.lock_heap = Lock()
        self.internal_threads = ThreadPoolExecutor(n_thread)
        self.futures: Deque[Future] = deque()

    def push(self, sorted_iterator: SortedIterator[Cost, Node]) -> None:
        """Push items to this heap"""
        self.futures.append(
            self.internal_threads.submit(
                self._internal_push, sorted_iterator,
            )
        )

    def stop(self) -> None:
        for fut in self.futures:
            fut.cancel()
        self.internal_threads.shutdown()

    def pop(self) -> Optional[Tuple[Cost, Node]]:
        """Pop the minimum cost item from this heap"""
        while True:
            # break condition and data race resolution
            # A little bit cryptic?
            self.lock_heap.acquire()  # pylint: disable=R1732
            if not self.heap:
                if len(self.futures) == 0:
                    return None
                self.lock_heap.release()
                while self.futures:
                    fut = self.futures.popleft()
                    if fut.done():
                        continue
                    _ = self.futures.popleft().result()
                    break
                continue
            self.lock_heap.release()

            # Do pop and re-register the iterator
            with self.lock_heap:
                cost, _, node, rest = heappop(self.heap)
                self.futures.append(
                    self.internal_threads.submit(
                        self._internal_push, rest,
                    )
                )

            return (cost, node)

    def _internal_push(self, sorted_iterator: SortedIterator[Cost, Node]):
        try:
            cost_next, node_next = next(sorted_iterator)
            with self.lock_heap:
                heappush(self.heap, (cost_next, self.index, node_next, sorted_iterator))
                self.index += 1
        except StopIteration:
            pass

    push.__doc__ = LazyHeap.push.__doc__
    pop.__doc__ = LazyHeap.pop.__doc__
