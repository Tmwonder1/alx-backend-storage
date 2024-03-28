#!/usr/bin/env python3
"""
web cache and tracker
"""

import redis
import requests
import time

# Initialize Redis client
r = redis.Redis()


def count_url_access(method):
    """Decorator counting how many times a URL is accessed"""
    def wrapper(url):
        # Generate keys for cache and counter
        count_key = "count:" + url

        # Increment access count for the URL
        r.incr(count_key)

        # Call the method to get HTML content
        html_content = method(url)

        # Cache the HTML content with expiration time of 10 seconds
        cache_key = "cached:" + url
        r.setex(cache_key, html_content, 10)

        return html_content
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Obtain the HTML content of a particular URL"""
    res = requests.get(url)
    return res.text


if __name__ == "__main__":
    # Test the function with a slow response URL
    print(get_page('http://slowwly.robertomurray.co.uk'))

    # Test caching behavior
    print(get_page('http://slowwly.robertomurray.co.uk'))

    # Verify count increment
    count_key = "count:http://slowwly.robertomurray.co.uk"
    print("Count:", r.get(count_key))
