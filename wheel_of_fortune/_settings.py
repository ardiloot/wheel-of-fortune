import os
import json
import asyncio
import logging
import aiofiles
from typing import Any


_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Settings",
    "SettingsManager",
]


class SettingsManager:
    def __init__(self, filename):
        self._filename: str = filename
        self._data: dict[str, Any] = {}
        self._saved: bool = False
        self._lock = asyncio.Lock()

    async def open(self):
        async with self._lock:
            _LOGGER.info("Open settings (%s)" % (self._filename))

            if not os.path.isfile(self._filename):
                _LOGGER.warning("Settings file not found: %s", self._filename)
                self._data = {}
                self._saved = True
                return

            async with aiofiles.open(self._filename, mode="r") as f:
                contents = await f.read()
            self._data = json.loads(contents)
            self._saved = True

    async def close(self):
        await self.save()

    async def save(self):
        async with self._lock:
            if self._saved:
                return
            _LOGGER.info("Save settings (%s)" % (self._filename))
            async with aiofiles.open(self._filename, mode="w") as f:
                await f.write(json.dumps(self._data, indent=4))
            self._saved = True

    async def maintain(self):
        while True:
            await self.save()
            await asyncio.sleep(10.0)

    def subsettings(self, name):
        return Settings(self, base_key=[name])

    def invalidate(self):
        self._saved = False

    def __getitem__(self, key):
        return self.subsettings(key)

    @property
    def data(self):
        return self._data


class Settings:
    def __init__(self, manager, base_key=[]):
        self._manager: SettingsManager = manager
        self._base_key = base_key

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        return self.set(key, value)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        _LOGGER.info(
            "Set setting (%s): %s = %s"
            % ("/".join(["%s" % (k) for k in self._base_key]), key, value)
        )
        self.data[key] = value
        self._manager.invalidate()

    def subsettings(self, name):
        return Settings(self._manager, base_key=self._base_key + [name])

    def invalidate(self):
        self._manager.invalidate()

    @property
    def data(self):
        res = self._manager.data
        for k in self._base_key:
            if k not in res:
                res[k] = {}
            res = res[k]
        return res
