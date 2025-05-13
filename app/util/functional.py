from inspect import iscoroutinefunction


class Pipe:
    def __init__(self, value):
        self.value = value

    async def __or__(self, func):
        if iscoroutinefunction(func):
            self.value = await func(self.value)
            return self
        self.value = func(self.value)
        return self


async def async_map(func, iterable):
    return [await func(x) for x in iterable]
