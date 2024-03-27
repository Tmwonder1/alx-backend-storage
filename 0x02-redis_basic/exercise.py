#!/usr/bin/env python3

"""
Cache class for storing data using Redis.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Represents a cache using Redis.
    """

    def __init__(self) -> None:
        """Initializes the Cache object."""
        self.redis = redis.Redis()
        self.redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in the cache and returns the key.

        Args:
            data: Data to be stored in the cache.

        Returns:
            str: Key used to store the data.
        """
        key = str(uuid.uuid4())
        self.redis.set(key, data)
        return key
