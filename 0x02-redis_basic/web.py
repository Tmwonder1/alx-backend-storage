#!/usr/bin/env python3
"""
Web cache and tracker
"""
import requests
import redis
from functools import wraps

# Initialize Redis client
store = redis.Redis()


def count_url_access(method):
    """Decorator counting how many times a URL is accessed"""

    @wraps(method)
    def wrapper(url):
        # Generate keys for cache and counter
        cached_key = "cached:" + url
        count_key = "count:" + url

        # Check if URL is cached
        cached_data = store.get(cached_key)
        if cached_data:
            # If cached, return cached HTML content
            return cached_data.decode("utf-8")

        # If not cached, retrieve HTML content from URL
        html = method(url)

        # Increment access count for the URL
        store.incr(count_key)

        # Cache the HTML content with expiration time of 10 seconds
        store.set(cached_key, html)
        store.expire(cached_key, 10)

        return html
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Returns HTML content of a URL"""
    res = requests.get(url)
    return res.text
