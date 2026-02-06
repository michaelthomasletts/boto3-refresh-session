# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Cache primitives for memoizing objects."""

__all__ = ["ClientCache", "ClientCacheKey"]

from collections import OrderedDict
from collections.abc import Iterator
from threading import RLock
from typing import Any, Tuple

from botocore.client import BaseClient
from botocore.config import Config

from ..exceptions import (
    BRSCacheError,
    BRSCacheExistsError,
    BRSCacheNotFoundError,
)


def _freeze_value(value: Any) -> Any:
    """Recursively freezes a value for use in cache keys.

    Parameters
    ----------
    value : Any
        The value to freeze.

    Returns
    -------
    Any
        A hashable representation of the value.
    """

    match value:
        # recursively freezing dicts
        case dict():
            return tuple(
                sorted((key, _freeze_value(val)) for key, val in value.items())
            )

        # recursively freezing lists and tuples
        case list() | tuple():
            return tuple(_freeze_value(item) for item in value)

        # recursively freezing sets
        case set():
            return tuple(sorted(_freeze_value(item) for item in value))

        # everything else remains unchanged
        case _:
            return value


def _config_cache_key(config: Config | None) -> Any:
    """Generates a cache key for a botocore.config.Config object.

    Parameters
    ----------
    config : Config | None
        The Config object to generate a cache key for.

    Returns
    -------
    Any
        A hashable representation of the Config object for use in cache keys.
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

    Returns
    -------
    str
        The formatted string representation of the value.
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
    boto3 client.

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
        """Creates the cache key and label based on the provided arguments.

        Parameters
        ----------
        *args : Any
            Positional arguments used to create the cache key.
        **kwargs : Any
            Keyword arguments used to create the cache key.
        """

        # creating a readable label for debugging purposes
        self.label: str = ", ".join(
            [
                *(repr(a) for a in args),
                *(
                    f"{k}={_format_label_value(v)}"
                    for k, v in sorted(kwargs.items())
                ),
            ]
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


class ClientCache:
    """A thread-safe LRU cache for storing clients which can be used exactly
    like a dictionary.

    Clients stored in this cache must be hashable. The cache has a maximum size
    attribute, and retrieved and newly added clients are marked as recently
    used. When the cache exceeds its maximum size, the least recently used
    client is evicted. When setting a client, use :class:`ClientCacheKey` for
    the key, not ``*args`` and ``**kwargs`` unless calling this class via
    ``__call__``.

    Editing the max size of the cache after initialization is supported, and
    will evict least recently used items until the cache size is within the
    new limit if the new maximum size is less than the current number of items
    in the cache.

    Attempting to overwrite an existing client in the cache will raise an
    error.

    ``ClientCache`` does not support ``fromkeys``, ``update``, ``setdefault``,
    the ``|=`` operator, or the ``|`` operator.

    Parameters
    ----------
    max_size : int, optional
        The maximum number of clients to store in the cache. Defaults to 10.

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
    """

    def __init__(self, max_size: int | None = None) -> None:
        self._max_size = abs(max_size if max_size is not None else 10)
        self._cache: OrderedDict[ClientCacheKey, BaseClient] = OrderedDict()
        self._lock = RLock()

    @property
    def max_size(self) -> int:
        """The maximum number of clients to store in the cache."""

        return self._max_size

    @max_size.setter
    def max_size(self, value: int) -> None:
        """Sets the maximum size of the cache. If the new maximum size is less
        than the current number of items in the cache, the least recently used
        items will be evicted until the cache size is within the new limit.

        Parameters
        ----------
        value : int
            The new maximum size for the cache.
        """

        with self._lock:
            self._max_size = abs(value)
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

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

        >>> cache = ClientCache(max_size=10)
        >>> s3_client = boto3.client("s3")
        >>> cache(s3_client, "s3", region_name="us-west-2")
        """

        self.__setitem__(ClientCacheKey(*args, **kwargs), obj)

    def __str__(self) -> str:
        with self._lock:
            if not self._cache:
                return "ClientCache(empty)"
            labels = "\n   ".join(
                f"- RefreshableSession.client({key.label})"
                for key in self._cache.keys()
            )
            return f"ClientCache:\n   {labels}"

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __reversed__(self) -> Iterator[ClientCacheKey]:
        with self._lock:
            return iter(tuple(reversed(self._cache.keys())))

    def __contains__(self, key: ClientCacheKey) -> bool:
        with self._lock:
            return key in self._cache

    def __iter__(self) -> Iterator[ClientCacheKey]:
        with self._lock:
            return iter(tuple(self._cache.keys()))

    def __getitem__(self, key: ClientCacheKey) -> BaseClient:
        with self._lock:
            # move obj to end of cache to mark it as recently used
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
            else:
                raise BRSCacheNotFoundError(
                    "The client you requested has not been cached."
                ) from None

    def __setitem__(self, key: ClientCacheKey, obj: BaseClient) -> None:
        if not isinstance(key, ClientCacheKey):
            raise BRSCacheError(
                "Cache key must be of type 'ClientCacheKey'."
            ) from None

        if not isinstance(obj, BaseClient):
            raise BRSCacheError(
                f"Cache value must be a boto3 client object, {type(obj)} "
                "provided."
            ) from None

        with self._lock:
            if key in self._cache:
                raise BRSCacheExistsError(
                    "Client already exists in cache."
                ) from None

            # setting the object
            self._cache[key] = obj
            # marking the object as recently used
            self._cache.move_to_end(key)

            # removing least recently used object if cache exceeds max size
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def __delitem__(self, key: ClientCacheKey) -> None:
        with self._lock:
            if key not in self._cache:
                raise BRSCacheNotFoundError(
                    "Client not found in cache."
                ) from None
            del self._cache[key]

    def keys(self) -> Tuple[ClientCacheKey, ...]:
        """Returns the keys in the cache."""

        with self._lock:
            return tuple(self._cache.keys())

    def values(self) -> Tuple[BaseClient, ...]:
        """Returns the values from the cache."""

        with self._lock:
            return tuple(self._cache.values())

    def items(self) -> Tuple[Tuple[ClientCacheKey, BaseClient], ...]:
        """Returns the items in the cache as (ClientCacheKey, BaseClient)
        tuples."""

        with self._lock:
            return tuple(self._cache.items())

    def get(
        self, key: ClientCacheKey, default: BaseClient | None = None
    ) -> BaseClient | None:
        """Gets the object using the given key, or returns the default."""

        with self._lock:
            # move obj to end of cache to mark it as recently used
            if key in self._cache:
                self._cache.move_to_end(key)
            return self._cache.get(key, default)

    def pop(self, key: ClientCacheKey) -> BaseClient:
        """Pops and returns the object associated with the given key."""

        with self._lock:
            if (obj := self._cache.get(key)) is None:
                raise BRSCacheNotFoundError(
                    "Client not found in cache."
                ) from None
            del self._cache[key]
            return obj

    def clear(self) -> None:
        """Clears all items from the cache."""

        with self._lock:
            self._cache.clear()

    def popitem(self) -> Tuple[ClientCacheKey, BaseClient]:
        """Pops and returns the least recently used item from the cache."""

        with self._lock:
            if not self._cache:
                raise BRSCacheNotFoundError(
                    "No clients found in cache."
                ) from None
            return self._cache.popitem(last=False)

    def copy(self) -> "ClientCache":
        """Returns a shallow copy of the cache."""

        with self._lock:
            new_cache = ClientCache(max_size=self.max_size)
            new_cache._cache = self._cache.copy()
            return new_cache
