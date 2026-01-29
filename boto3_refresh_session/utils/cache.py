# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Cache primitives for memoizing objects."""

__all__ = ["BaseCache", "LFUClientCache", "LRUClientCache", "ClientCacheKey"]

from abc import ABC, abstractmethod
from threading import RLock
from typing import Any, Iterable, Literal

from botocore.client import BaseClient
from botocore.config import Config

from ..exceptions import (
    BRSCacheError,
    BRSCacheExistsError,
    BRSCacheNotFoundError,
)
from .data_structures import DoublyLinkedList, ListNode

CacheTrackingList = DoublyLinkedList["ClientCacheKey"]
CacheTrackingNode = ListNode["ClientCacheKey"]


def _freeze_value(value: Any) -> Any:
    """Recursively freezes a value for use in cache keys.

    Parameters
    ----------
    value : Any
        The value to freeze.
    """

    # recursively freezing dicts
    if isinstance(value, dict):
        return tuple(
            sorted((key, _freeze_value(val)) for key, val in value.items()),
        )

    # recursively freezing lists and tuples
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)

    # recursively freezing sets
    if isinstance(value, set):
        return tuple(sorted(_freeze_value(item) for item in value))

    return value


def _config_cache_key(config: Config | None) -> Any:
    """Generates a cache key for a botocore.config.Config object.

    Parameters
    ----------
    config : Config | None
        The Config object to generate a cache key for.
    """

    if config is None:
        return None

    # checking for user-provided options first
    options = getattr(config, "_user_provided_options", None)
    if options is None:
        # __dict__ is pedantic but stable
        return _freeze_value(getattr(config, "__dict__", {}))

    return _freeze_value(options)


def _format_label_value(value: Any) -> str:
    """Formats a value for use in cache key labels.

    Parameters
    ----------
    value : Any
        The value to format.
    """

    if isinstance(value, Config):
        # checking for user-provided options first
        options = getattr(value, "_user_provided_options", None)

        # falling back to __dict__ if no user-provided options exist
        if options is None:
            options = getattr(value, "__dict__", {})

        # creating a sorted string representation of the options
        options = ", ".join([f"{k}={v!r}" for k, v in sorted(options.items())])
        return f"Config({options})"

    return repr(value)


class ClientCacheKey:
    """A unique, hashable key for caching clients based on their
    initialization parameters.

    In order to interact with the cache, instances of this class should be
    created using the same arguments that would be used to initialize the
    client.

    Parameters
    ----------
    *args : Any
        Positional arguments used to create the cache key.
    **kwargs : Any
        Keyword arguments used to create the cache key.

    Attributes
    ----------
    key : tuple
        The unique key representing the client's initialization parameters.
    label : str
        A human-readable label for the cache key, useful for debugging.
    """

    def __init__(self, *args, **kwargs) -> None:
        # initializing the cache key and label
        self._create(*args, **kwargs)

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"ClientCacheKey(RefreshableSession.client({self.label}))"

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ClientCacheKey) and self.key == other.key

    def _create(self, *args, **kwargs) -> None:
        # creating a readable label for debugging purposes
        self.label: str = ", ".join(
            [
                *(repr(a) for a in args),
                *(
                    f"{k}={_format_label_value(v)}"
                    for k, v in sorted(kwargs.items())
                ),
            ],
        )

        # checking if Config was passed as a positional arg
        _args = [
            _config_cache_key(arg) if isinstance(arg, Config) else arg
            for arg in args
        ]

        # popping trailing None values from args, preserving None in middle
        while _args and _args[-1] is None:
            _args.pop()
        _args = tuple(_args)

        # checking if Config was passed as a keyword arg
        _kwargs = kwargs.copy()
        if _kwargs.get("config") is not None:
            _kwargs["config"] = _config_cache_key(_kwargs["config"])

        # preemptively removing None values from kwargs
        _kwargs = {
            key: value for key, value in _kwargs.items() if value is not None
        }

        # creating a unique key for the client cache
        self.key = (_args, tuple(sorted(_kwargs.items())))


class _CacheItem:
    """Provides an indirection layer between a cache dict and an item in the
    cache, primarily for carrying a reference to a tracking object.
    """

    data: BaseClient
    tracking_node: CacheTrackingNode

    def __init__(self, *, data: BaseClient, tracking_node: CacheTrackingNode):
        self.data = data
        self.tracking_node = tracking_node


class BaseCache(ABC):
    """A thread-safe cache for storing clients which can be used like a
    dictionary.

    Clients stored in the cache must be hashable. The cache has a maximum size
    attribute, and retrieved and newly added clients are marked as recently
    used. When the cache exceeds its maximum size, the least recently used
    client is evicted. When setting a client, use :class:`ClientCacheKey` for
    the key, not ``*args`` and ``**kwargs`` unless calling this class via
    ``__call__``.

    Parameters
    ----------
    max_size : int, optional
        The maximum number of clients to store in the cache. Defaults to 10.
    """

    def __init__(self, max_size: int | None = None):
        self.max_size = abs(max_size if max_size is not None else 10)
        self._cache: dict[ClientCacheKey, _CacheItem] = dict()
        self._tracking: CacheTrackingList = CacheTrackingList()
        self._lock = RLock()

    def __call__(self, obj: BaseClient, *args, **kwargs) -> None:
        """Adds the given object to the cache using the provided arguments to
        create the cache key.

        Parameters
        ----------
        obj : BaseClient
            The client object to cache.
        *args : Any
            Positional arguments used to create the cache key.
        **kwargs : Any
            Keyword arguments used to create the cache key.

        Examples
        --------
        Using the ClientCache to cache an S3 client:

        >>> cache = LRUClientCache(max_size=10)
        >>> s3_client = boto3.client("s3")
        >>> cache(s3_client, "s3", region_name="us-west-2")
        """

        self.__setitem__(ClientCacheKey(*args, **kwargs), obj)

    def __str__(self) -> str:
        with self._lock:
            if not self._cache:
                return "ClientCache(empty)"
            labels = "\n   ".join(
                [
                    f"- RefreshableSession.client({key.label})"
                    for key in self._cache.keys()
                ],
            )
            return f"ClientCache:\n   {labels}"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: ClientCacheKey) -> bool:
        with self._lock:
            return key in self._cache

    def __getitem__(self, key: ClientCacheKey) -> BaseClient:
        if (value := self.get(key)) is None:
            raise BRSCacheNotFoundError("Client not found in cache.")
        return value

    def __iter__(self) -> Iterable[tuple[ClientCacheKey, BaseClient]]:
        with self._lock:
            return iter(tuple(self._cache.keys()))

    def __setitem__(self, key: ClientCacheKey, obj: BaseClient) -> None:
        self.set(key, obj)

    @staticmethod
    def new(
        max_size: int = None, strategy: Literal["lru", "lfu"] | None = None
    ) -> "LRUClientCache | LFUClientCache":
        if strategy is None:
            strategy = "lru"
        match strategy:
            case "lru":
                return LRUClientCache(max_size=max_size)
            case "lfu":
                return LFUClientCache(max_size=max_size)
            case _:
                raise BRSCacheError(
                    "Strategy not supported, must be lru or lfu"
                )

    @abstractmethod
    def get(
        self,
        key: ClientCacheKey,
        default: BaseClient | None = None,
    ) -> BaseClient | None:
        """Gets the object using the given key, or returns None if no
        default is provided.

        Parameters
        ----------
        key : ClientCacheKey
            The key to retrieve the object for.
        default : BaseClient | None, optional
            The default value to return if the key is not found. Defaults to
            None.
        """

        ...

    @abstractmethod
    def pop(self, key: ClientCacheKey) -> BaseClient:
        """Pops and returns the object using the given key.

        Parameters
        ----------
        key : ClientCacheKey
            The key to pop the object for.

        Returns
        -------
        BaseClient
            The popped client object.

        Raises
        ------
        BRSCacheNotFoundError
            Raised when attempting to pop a client which does not exist in the
            cache.
        """

        ...

    @abstractmethod
    def set(self, key: ClientCacheKey, value: BaseClient) -> None:
        """Adds the given key and value to the cache.

        Parameters
        ----------
        key : ClientCacheKey
            The cache key for the given client.
        value : BaseClient
            The client object to cache.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clears all items from the cache."""

        ...

    def keys(self) -> tuple[ClientCacheKey]:
        """Returns the keys in the cache."""

        with self._lock:
            return tuple(self._cache.keys())

    def values(self) -> tuple[BaseClient]:
        """Returns the objects from the cache."""

        with self._lock:
            return tuple(self._cache.values())

    def items(self) -> tuple[tuple[ClientCacheKey, BaseClient]]:
        """Returns the items in the cache as (hash, BaseClient) tuples."""

        with self._lock:
            return tuple(self._cache.items())


class LRUClientCache(BaseCache):
    """A thread-safe LFU cache for storing clients which can be used like a
    dictionary.

    Clients stored in the cache must be hashable. The cache has a maximum size
    attribute, and retrieved and newly added clients are marked as recently
    used. When the cache exceeds its maximum size, the least recently used
    client is evicted. When setting a client, use :class:`ClientCacheKey` for
    the key, not ``*args`` and ``**kwargs`` unless calling this class via
    ``__call__``.

    Raises
    ------
    BRSCacheExistsError
        Raised when attempting to add a client which already exists in the
        cache.
    BRSCacheNotFoundError
        Raised when attempting to retrieve or delete a client which does not
        exist in the cache.

    See Also
    --------
    boto3_refresh_session.utils.cache.ClientCacheKey

    Notes
    -----
    This class does not inherit from ``dict``. Therefore, some dictionary
    methods may not be available.
    """

    def get(
        self,
        key: ClientCacheKey,
        default: BaseClient | None = None,
    ) -> BaseClient | None:
        with self._lock:
            if key in self._cache:
                item = self._cache[key]

                # remove item's tracking node and append a new one to the end
                # of the tracking list to mark it as recently used
                self._tracking.move_to_end(item.tracking_node)

                # if the tracking head contains the key, replace the head with
                # the next node
                if self._tracking.head.data == {key}:
                    self._tracking.head = self._tracking.head.next_node

                return item.data
        return default

    def pop(self, key: ClientCacheKey) -> BaseClient:
        with self._lock:
            if (obj := self._cache.get(key)) is None:
                raise BRSCacheNotFoundError("Client not found in cache.")
            del self._cache[key]
            self._tracking.remove(obj.tracking_node)
            return obj.data

    def set(self, key: ClientCacheKey, value: BaseClient) -> None:
        if not isinstance(key, ClientCacheKey):
            raise BRSCacheError("Cache key must be of type 'ClientCacheKey'.")

        with self._lock:
            if key in self._cache:
                raise BRSCacheExistsError("Client already exists in cache.")

            # setting the object
            tracking_node = CacheTrackingNode(data={key})
            self._cache[key] = _CacheItem(
                data=value,
                tracking_node=tracking_node,
            )
            # marking the object as recently used
            self._tracking.append(tracking_node)

            # removing least recently used object if cache exceeds max size
            if len(self._cache) > self.max_size:
                first_key = self._tracking.head.data.pop()
                del self._cache[first_key]
                self._tracking.remove(self._tracking.head)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._tracking.clear()


class LFUClientCache(BaseCache):
    """A thread-safe LFU cache for storing clients which can be used like a
    dictionary.

    Clients stored in the cache must be hashable. The cache has a maximum
    size attribute, and retrieved and newly added clients are marked as
    recently used. When the cache exceeds its maximum size, the least
    recently used client is evicted. When setting a client,
    use :class:`ClientCacheKey` for the key, not ``*args`` and ``**kwargs``
    unless calling this class via ``__call__``.

    This class implements the Least Frequently Used (LFU) eviction strategy
    described by Matani et al. [1]. This algorithm features a runtime
    complexity of O(1) for insertion, access, and eviction, making its
    performance comparable to that of simpler strategies like Least Recently
    Used.

    One notable caveat is that, when the cache size reaches the maximum,
    newly-inserted items may be subsequently evicted. This can happen because
    frequency tracking is naively backed by a set, which does not preserve
    ordering in Python. If this becomes a problem, we can replace the set
    with a dict or doubly linked list to preserve ordering while maintaining
    the runtime performance characteristics of the current implementation.

    [1]: https://arxiv.org/abs/2110.11602

    Raises
    ------
    BRSCacheExistsError
        Raised when attempting to add a client which already exists in the
        cache.
    BRSCacheNotFoundError
        Raised when attempting to retrieve or delete a client which does not
        exist in the cache.

    See Also
    --------
    boto3_refresh_session.utils.cache.ClientCacheKey

    Notes
    -----
    This class does not inherit from ``dict``. Therefore, some dictionary
    methods may not be available.
    """

    def __init__(self, max_size: int | None = None):
        super().__init__(max_size)

    def get(
        self,
        key: ClientCacheKey,
        default: BaseClient | None = None,
    ) -> BaseClient | None:
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                frequency = item.tracking_node

                if not frequency.next_node:
                    frequency.next_node = CacheTrackingNode(
                        value=frequency.value + 1,
                        previous_node=frequency,
                        next_node=None,
                    )

                next_frequency = frequency.next_node

                if next_frequency.value != frequency.value + 1:
                    next_frequency = CacheTrackingNode(
                        value=frequency.value + 1,
                        previous_node=frequency,
                        next_node=next_frequency,
                    )

                next_frequency.data.add(key)
                item.tracking_node = next_frequency

                frequency.data.remove(key)
                if len(frequency.data) == 0:
                    self._tracking.remove(frequency)
                return item.data
        return default

    def set(self, key: ClientCacheKey, value: BaseClient):
        if not isinstance(key, ClientCacheKey):
            raise BRSCacheError("Cache key must be of type 'ClientCacheKey'.")

        with self._lock:
            if key in self._cache:
                raise BRSCacheExistsError("Client already exists in cache.")

            frequency = self._tracking.head
            if not frequency or frequency.value != 1:
                frequency = CacheTrackingNode(
                    value=1,
                    previous_node=self._tracking.head,
                    next_node=frequency,
                )
                self._tracking.head = frequency

            self._evict()
            frequency.data.add(key)
            self._cache[key] = _CacheItem(data=value, tracking_node=frequency)

    def _evict(self):
        if not len(self._cache) >= self.max_size:
            return

        current_node = self._tracking.head
        while True:
            if not current_node.data:
                current_node = current_node.next_node
            else:
                break
        key_to_delete = current_node.data.pop()
        del self._cache[key_to_delete]

        if not self._tracking.head.data:
            self._tracking.remove(self._tracking.head)

    def pop(self, key: ClientCacheKey) -> BaseClient:
        with self._lock:
            if (obj := self._cache.get(key)) is None:
                raise BRSCacheNotFoundError("Client not found in cache.")
            obj.tracking_node.data.remove(key)
            del self._cache[key]
            return obj.data

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._tracking.clear()
