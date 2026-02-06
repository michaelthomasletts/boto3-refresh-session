# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest
from botocore.client import BaseClient
from botocore.config import Config

from boto3_refresh_session import ClientCache, ClientCacheKey
from boto3_refresh_session.exceptions import (
    BRSCacheError,
    BRSCacheExistsError,
    BRSCacheNotFoundError,
)


def _client() -> BaseClient:
    return object.__new__(BaseClient)


def test_client_cache_key_normalizes_config() -> None:
    """Normalizes equivalent botocore Config values for cache keys."""
    config_a = Config(retries={"max_attempts": 2, "mode": "standard"})
    config_b = Config(retries={"mode": "standard", "max_attempts": 2})

    key_a = ClientCacheKey("s3", config=config_a)
    key_b = ClientCacheKey("s3", config=config_b)

    assert key_a == key_b
    assert hash(key_a) == hash(key_b)


def test_client_cache_evicts_lru() -> None:
    """Evicts least-recently-used entries when max size is exceeded."""
    cache = ClientCache(max_size=2)
    client_a = _client()
    client_b = _client()
    client_c = _client()

    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")
    key_c = ClientCacheKey("ec2")

    cache[key_a] = client_a
    cache[key_b] = client_b

    assert cache.get(key_a) is client_a
    cache[key_c] = client_c

    assert key_b not in cache
    assert key_a in cache
    assert key_c in cache


def test_client_cache_call_inserts() -> None:
    """Inserts an entry when invoking the cache as a callable."""
    cache = ClientCache(max_size=10)
    args = ("s3",)
    kwargs = {"region_name": "us-west-2"}

    client = _client()
    cache(client, *args, **kwargs)
    key = ClientCacheKey(*args, **kwargs)

    assert key in cache
    assert cache[key] is client


def test_client_cache_str_includes_entries() -> None:
    """Includes cached client entries in the string representation."""
    cache = ClientCache(max_size=10)
    cache(_client(), "s3")

    output = str(cache)
    assert output.startswith("ClientCache:")
    assert "RefreshableSession.client('s3')" in output
    assert "\n" in output


def test_client_cache_rejects_non_client_value() -> None:
    """Rejects cached values that are not botocore BaseClient instances."""
    cache = ClientCache(max_size=10)
    key = ClientCacheKey("s3")

    with pytest.raises(BRSCacheError, match="Cache value must be a boto3"):
        cache[key] = object()  # type: ignore[assignment]

    with pytest.raises(BRSCacheError, match="Cache value must be a boto3"):
        cache(object(), "s3")  # type: ignore[arg-type]


def test_client_cache_set_existing_key_raises() -> None:
    """Raises when attempting to cache a client under an existing key."""
    cache = ClientCache(max_size=10)
    key = ClientCacheKey("s3")

    cache[key] = _client()

    with pytest.raises(BRSCacheExistsError, match="already exists"):
        cache[key] = _client()


def test_client_cache_reversed_is_mru_to_lru() -> None:
    """Iterates keys from most-recently-used to least-recently-used."""
    cache = ClientCache(max_size=10)
    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")

    cache[key_a] = _client()
    cache[key_b] = _client()

    # touch A so it's MRU; order becomes B, A
    _ = cache[key_a]

    assert list(reversed(cache)) == [key_a, key_b]


def test_client_cache_popitem_pops_lru() -> None:
    """popitem removes and returns the least recently used entry."""
    cache = ClientCache(max_size=10)
    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")
    client_a = _client()
    client_b = _client()

    cache[key_a] = client_a
    cache[key_b] = client_b

    popped_key, popped_client = cache.popitem()
    assert (popped_key, popped_client) == (key_a, client_a)
    assert key_a not in cache
    assert key_b in cache


def test_client_cache_popitem_empty_raises() -> None:
    """popitem raises when the cache is empty."""
    cache = ClientCache(max_size=10)
    with pytest.raises(BRSCacheNotFoundError, match="No clients found"):
        cache.popitem()


def test_client_cache_copy_is_independent() -> None:
    """copy returns a new cache with the same contents."""
    cache = ClientCache(max_size=2)
    key_a = ClientCacheKey("s3")
    cache[key_a] = _client()

    copied = cache.copy()
    assert copied is not cache
    assert copied.max_size == cache.max_size
    assert copied.keys() == cache.keys()

    key_b = ClientCacheKey("sts")
    copied[key_b] = _client()
    assert key_b in copied
    assert key_b not in cache


def test_client_cache_max_size_normalizes_negative() -> None:
    """Normalizes negative max_size values to a positive integer."""
    cache = ClientCache(max_size=-3)
    assert cache.max_size == 3


def test_client_cache_shrinking_max_size_evicts_until_within_limit() -> None:
    """Evicts least-recently-used items when max_size is reduced."""
    cache = ClientCache(max_size=3)
    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")
    key_c = ClientCacheKey("ec2")

    cache[key_a] = _client()
    cache[key_b] = _client()
    cache[key_c] = _client()

    # Touch A so it becomes the most recently used.
    _ = cache[key_a]

    cache.max_size = 1

    assert len(cache) == 1
    assert key_a in cache
    assert key_b not in cache
    assert key_c not in cache
