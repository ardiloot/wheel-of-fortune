import os
import time
import asyncio
import logging
import pygame
from ._config import Config
from ._settings import Settings

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Sound",
]


class Sound:

    def __init__(self, config, settings):
        self._config: Config = config
        self._settings: Settings = settings
        self._volume = 0.5

        start = time.time()
        pygame.mixer.init()
        _LOGGER.info("init %.3f ms" % (1e3 * (time.time() - start)))

        # Decrypt and load sounds
        self._sounds = {}
        sounds_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sounds")
        _LOGGER.info("sounds_dir: %s" % (sounds_dir))

        suffix = ".mp3"
        for fname in os.listdir(sounds_dir):
            if not fname.endswith(suffix):
                _LOGGER.warn("unknown sound file: %s" % (fname))
                continue
            _LOGGER.info("loading sound file: %s" % (fname))

            sound = pygame.mixer.Sound(os.path.join(sounds_dir, fname))
            sound.set_volume(self._volume)
            name = fname[:-len(suffix)]
            self._sounds[name] = sound

        _LOGGER.info("init + load %.3f ms" % (1e3 * (time.time() - start)))

    async def open(self):
        _LOGGER.info("open")
        if "volume" in self._settings:
            await self.set_volume(self._settings["volume"], save=False)

    async def close(self):
        _LOGGER.info("close")
        pygame.mixer.quit()

    async def set_volume(self, volume: float, save=True):
        self._volume = volume
        for sound in self._sounds.values():
            sound.set_volume(self._volume)
        if save:
            self._settings["volume"] = volume

    async def play_sound(self, name):
        start = time.time()
        res = self._sounds[name].play()
        _LOGGER.info("play %s in %.3f ms" % (name, 1e3 * (time.time() - start)))
        return res

    async def stop_sound(self, name):
        start = time.time()
        res = self._sounds[name].stop()
        _LOGGER.info("stop %s in %.3f ms" % (name, 1e3 * (time.time() - start)))
        return res

    async def fadeout_all(self, timeout_ms=300):
        start = time.time()
        pygame.mixer.fadeout(timeout_ms)
        _LOGGER.info("fadeout_all %.3f ms" % (1e3 * (time.time() - start)))

    async def set_state(self, volume=None):
        if volume is not None:
            await self.set_volume(volume)

    async def get_state(self):
        _LOGGER.info("Get state")

        sounds_state = {}
        for name, sound in self._sounds.items():
            sounds_state[name] = {
                "volume": sound.get_volume(),
                "num_playing": sound.get_num_channels(),
                "duration_secs": sound.get_length(),
            }

        return {
            "inited": pygame.mixer.get_init() is not None,
            "volume": self._volume,
            "num_channels": pygame.mixer.get_num_channels(),
            "is_busy": pygame.mixer.get_busy(),
            "sounds": sounds_state,
        }
        
    async def maintain(self):
        while True:
            # _LOGGER.debug("busy: %d, channels: %d" % (
            #     pygame.mixer.get_busy(),
            #     pygame.mixer.get_num_channels()
            # ))
            await asyncio.sleep(2.0)
