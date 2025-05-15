async def async_map(func, iterable):
    return [await func(x) for x in iterable]
