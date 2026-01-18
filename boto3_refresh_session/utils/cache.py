# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Cache primitives for memoizing boto3 client instances.

`ClientCache` provides a thread-safe mapping for cached clients and raises
`BRSCacheError` when lookups or mutations violate the expected cache contract.
"""

__all__ = ["ClientCache"]

from threading import Lock
from typing import Hashable, Optional

from botocore.client import BaseClient

from ..exceptions import BRSCacheExistsError, BRSCacheNotFoundError


class ClientCache:
    """A thread-safe cache for storing boto3 clients which can be used like a
    dictionary."""

    def __init__(self):
        self._cache: dict[Hashable, BaseClient] = {}
        self._lock = Lock()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __contains__(self, hash: Hashable) -> bool:
        with self._lock:
            return hash in self._cache

    def __iter__(self):
        with self._lock:
            return iter(self._cache.keys())

    def __getitem__(self, hash: Hashable) -> BaseClient:
        with self._lock:
            try:
                return self._cache[hash]
            except KeyError as err:
                raise BRSCacheNotFoundError(
                    "The client you requested has not been cached."
                ) from err

    def __setitem__(self, hash: Hashable, client: BaseClient) -> None:
        with self._lock:
            if hash in self._cache:
                raise BRSCacheExistsError("Client already exists in cache.")

            self._cache[hash] = client

    def __delitem__(self, hash: Hashable) -> None:
        with self._lock:
            if hash not in self._cache:
                raise BRSCacheNotFoundError("Client not found in cache.")
            del self._cache[hash]

    def keys(self) -> tuple[Hashable, ...]:
        """Returns the keys in the cache."""

        with self._lock:
            return tuple(self._cache.keys())

    def values(self) -> tuple[BaseClient, ...]:
        """Returns the clients from the cache."""

        with self._lock:
            return tuple(self._cache.values())

    def items(self) -> tuple[tuple[Hashable, BaseClient], ...]:
        """Returns the items in the cache as (hash, BaseClient) tuples."""

        with self._lock:
            return tuple(self._cache.items())

    def get(
        self, hash: Hashable, default: Optional[BaseClient] = None
    ) -> Optional[BaseClient]:
        """Gets the client using the given signature, or returns None if no
        default is provided.
        """

        with self._lock:
            return self._cache.get(hash, default)

    def pop(self, hash: Hashable) -> BaseClient:
        """Pops and returns the client using the given signature."""

        with self._lock:
            if (client := self._cache.get(hash)) is None:
                raise BRSCacheNotFoundError("Client not found in cache.")
            del self._cache[hash]
            return client
