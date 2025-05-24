from asyncio import sleep


def offset_coroutine(coroutine, offset):
    async def wrapper():
        await sleep(offset)
        return await coroutine

    return wrapper()
