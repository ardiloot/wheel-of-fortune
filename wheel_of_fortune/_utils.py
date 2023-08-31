import asyncio
import logging
from typing import Callable

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "decode_grey_code",
    "encode_gray_code",
    "AsyncTimer",
]


def decode_grey_code(num: int) -> int:
    res = num
    mask = res >> 1
    while mask > 0:
        res ^= mask
        mask >>= 1
    return res


def encode_gray_code(num: int) -> int:
    return num ^ (num >> 1)


class AsyncTimer:
    def __init__(self, timeout: float, callback):
        self._callback: Callable[[], None] = callback
        self._timeout: float = timeout
        self._task: asyncio.Task | None = None

    def start(self):
        self.cancel()
        self._task = asyncio.create_task(self._run())

    def cancel(self):
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def _run(self):
        try:
            await asyncio.sleep(self._timeout)
            self._callback()
        except Exception:
            _LOGGER.exception("Error in timer callback")
