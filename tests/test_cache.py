# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from botocore.config import Config

from boto3_refresh_session.utils.cache import (
    LRUClientCache,
    ClientCacheKey,
    LFUClientCache,
)


def test_client_cache_key_normalizes_config() -> None:
    config_a = Config(retries={"max_attempts": 2, "mode": "standard"})
    config_b = Config(retries={"mode": "standard", "max_attempts": 2})

    key_a = ClientCacheKey("s3", config=config_a)
    key_b = ClientCacheKey("s3", config=config_b)

    assert key_a == key_b
    assert hash(key_a) == hash(key_b)


def test_client_cache_evicts_lru() -> None:
    cache = LRUClientCache(max_size=2)
    obj_a = object()
    obj_b = object()
    obj_c = object()

    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")
    key_c = ClientCacheKey("ec2")

    cache[key_a] = obj_a
    cache[key_b] = obj_b

    assert cache.get(key_a) is obj_a
    cache[key_c] = obj_c

    assert key_b not in cache
    assert key_a in cache
    assert key_c in cache


def test_client_cache_evicts_lfu() -> None:
    cache = LFUClientCache(max_size=2)
    obj_a = object()
    obj_b = object()
    obj_c = object()

    key_a = ClientCacheKey("s3")
    key_b = ClientCacheKey("sts")
    key_c = ClientCacheKey("ec2")

    cache[key_a] = obj_a
    cache[key_b] = obj_b

    for _ in range(5):
        assert cache.get(key_a) is obj_a

    cache[key_c] = obj_c

    assert key_b not in cache
    assert key_a in cache
    assert key_c in cache


def test_client_cache_call_inserts() -> None:
    cache = LRUClientCache(max_size=10)
    obj = object()
    args = ("s3",)
    kwargs = {"region_name": "us-west-2"}

    cache(obj, *args, **kwargs)
    key = ClientCacheKey(*args, **kwargs)

    assert key in cache
    assert cache[key] is obj


def test_client_cache_str_includes_entries() -> None:
    cache = LRUClientCache(max_size=10)
    cache(object(), "s3")

    output = str(cache)
    assert output.startswith("ClientCache:")
    assert "RefreshableSession.client('s3')" in output
    assert "\n" in output
