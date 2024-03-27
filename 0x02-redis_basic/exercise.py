#!/usr/bin/env python3
"""Module declares a redis class and methods"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''Decorator to count how many times methods of Cache class are called'''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrap the decorated function and return the wrapper'''
        # Increment the call count
        self._redis.incr(method.__qualname__)
        # Call the method and return its result
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''Store the history of inputs and outputs for a particular function'''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrap the decorated function and return the wrapper'''
        # Store the input
        input_data = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input_data)
        # Call the method
        output_data = method(self, *args, **kwargs)
        # Store the output
        self._redis.rpush(method.__qualname__ + ":outputs", str(output_data))
        return output_data
    return wrapper


def replay(fn: Callable):
    '''Display the history of calls of a particular function'''
    # Connect to Redis
    r = redis.Redis()
    # Get the function name
    func_name = fn.__qualname__
    # Get the call count
    call_count = int(r.get(func_name) or 0)
    print(f"{func_name} was called {call_count} times:")
    # Retrieve inputs and outputs from Redis
    inputs = r.lrange(f"{func_name}:inputs", 0, -1)
    outputs = r.lrange(f"{func_name}:outputs", 0, -1)
    # Display inputs and outputs
    for inp, outp in zip(inputs, outputs):
        print(f"{func_name}(*{inp.decode('utf-8')}) -> {outp.decode('utf-8')}")


class Cache:
    '''Declares a Cache redis class'''
    def __init__(self):
        '''Upon initialization, store an instance and flush'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Store data in the cache and return a string'''
        # Generate a random key
        key = str(uuid4())
        # Store the data in Redis
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''Retrieve data from the cache by key'''
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''Retrieve a string data from the cache by key'''
        value = self._redis.get(key)
        return value.decode("utf-8") if value else ''

    def get_int(self, key: str) -> int:
        '''Retrieve an integer data from the cache by key'''
        value = self._redis.get(key)
        return int(value.decode("utf-8")) if value else 0
