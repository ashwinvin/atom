from functools import partial, wraps
import asyncio
import functools


def executor(loop=None):
    loop = loop or asyncio.get_event_loop()

    def inner(func):
        @wraps(func)
        def function(*args, **kwargs):
            fpartial = partial(func, *args, **kwargs)
            return loop.run_in_executor(None, fpartial)

        return function

    return inner
