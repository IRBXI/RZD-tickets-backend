async def async_map(func, iterable):
    return [await func(x) async for x in iterable]
