from threading import RLock
from typing import Generic, Hashable, TypeVar

__all__ = ["ListNode", "DoublyLinkedList"]

_KT = TypeVar("_KT", bound=Hashable)


class ListNode(Generic[_KT]):
    """A linear, thread-safe collection of ListNodes with forward and backward
    references.

    Parameters
    ----------
    value : int
        TODO
    items : set, optional
        TODO
    previous_node : ListNode, optional
        TODO
    next_node : ListNode, optional
        TODO
    """

    def __init__(
        self,
        value: int | None = None,
        items: set[_KT] | None = None,
        previous_node: "ListNode | None" = None,
        next_node: "ListNode | None" = None,
    ):
        self.value = value
        self.items = set() if items is None else items
        self.previous_node = previous_node
        self.next_node = next_node

        if self.previous_node:
            self.previous_node.next_node = self
        if self.next_node:
            self.next_node.previous_node = self

    def __str__(self) -> str:
        return ", ".join(self.items)

    def __repr__(self) -> str:
        return f"ListNode({str(self)})"


class DoublyLinkedList(Generic[_KT]):
    """A linear, thread-safe collection of ListNodes with forward and backward
    references.

    Attributes
    ----------
    head : ListNode
        TODO
    tail : ListNode
        TODO
    """

    def __init__(self):
        self.head: ListNode | None = None
        self.tail: ListNode | None = None
        self._lock: RLock = RLock()

    def __iter__(self):
        with self._lock:
            current_head = self.head
            while True:
                if not current_head:
                    break
                yield current_head
                current_head = current_head.next_node

    def clear(self):
        """Set the doubly linked list's head and tail to None, effectively
        clearing the list.
        """
        with self._lock:
            self.head = None
            self.tail = None

    def remove(self, node: ListNode[_KT]):
        """Remove a node from the doubly linked list by updating its adjacent
        nodes' references to point at each other.
        """
        with self._lock:
            if node.previous_node:
                node.previous_node.next_node = node.next_node
            else:
                self.head = node.next_node
            if node.next_node:
                node.next_node.previous_node = node.previous_node
            else:
                self.tail = node.previous_node

    def move_to_end(self, node: ListNode[_KT]):
        """Remove the given node and re-add it as the tail of the doubly linked
        list.
        """
        with self._lock:
            self.remove(node)
            self.append(node)

    def append(self, node: ListNode[_KT]):
        """Add a new node as the tail of the doubly linked list."""
        with self._lock:
            new_tail = node
            current_tail = self.tail

            if current_tail is not None:
                current_tail.next_node = new_tail
                new_tail.previous_node = current_tail

            new_tail.next_node = None
            self.tail = new_tail

            if self.head is None:
                self.head = new_tail

    def prepend(self, node: ListNode[_KT]):
        """Add a new node as the head of the doubly linked list."""
        with self._lock:
            new_head = node
            current_head = self.head

            if current_head is not None:
                current_head.previous_node = new_head
                new_head.next_node = current_head

            new_head.previous_node = None
            self.head = new_head

            if self.tail is None:
                self.tail = new_head
