#

import dataclasses
import functools
import time


def ttl_cache(ttl=60, typed=False):
    make_key = functools._make_key

    @dataclasses.dataclass
    class Cache:
        expiration: float
        value: object

    def decorator(func):
        func.cache = {}

        def clear():
            func.cache.clear()

        def get(*args, default=None, **kwargs):
            sentinel = object()
            key = make_key(args, kwargs, typed=typed)

            cache = func.cache.get(key, sentinel)

            if cache is sentinel:
                return default

            if cache.expiration < time.monotonic():
                del func.cache[key]
                return default

            return cache

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sentinel = object()
            cached = get(*args, default=sentinel, **kwargs)

            if cached is sentinel:
                # NOTE(jkoelker) Run the func prior to expiration calculation.
                value = func(*args, **kwargs)

                cached = Cache(
                    expiration=time.monotonic() + ttl,
                    value=value,
                )

                key = make_key(args, kwargs, typed=typed)
                func.cache[key] = cached

            return cached.value

        wrapper.get = get
        wrapper.clear = clear

        return wrapper

    return decorator
