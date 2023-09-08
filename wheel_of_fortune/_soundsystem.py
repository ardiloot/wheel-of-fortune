import os
import asyncio
import logging
import pygame.mixer
import time
from typing import Callable
from ._config import Config
from ._settings import Settings
from .schemas import (
    SoundChannelState,
    SoundChannelStateIn,
    SoundInfo,
    SoundSystemState,
    SoundSystemStateIn,
    SoundSystemInfo,
)

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "SoundSystem",
    "MAIN_CH",
    "EFFECT_CH",
]

MAIN_CH = "main"
EFFECT_CH = "effect"


class SoundChannel:
    def __init__(self, channel, sounds, settings):
        self._channel: pygame.mixer.Channel = channel
        self._sounds: dict[str, pygame.mixer.Sound] = sounds
        self._settings: Settings = settings

        self._volume: float = 0.1
        self._sound_name: str | None = None

    def open(self):
        if "volume" in self._settings:
            self._volume = self._settings["volume"]
        self._channel.set_volume(self._volume)

    async def set_state(self, state: SoundChannelStateIn):
        if state.volume is not None:
            self._volume = state.volume
            self._channel.set_volume(self._volume)
            self._settings["volume"] = self._volume

        if state.sound_name is not None:
            await self.play(state.sound_name)

    def get_state(self) -> SoundChannelState:
        return SoundChannelState(
            volume=self._volume,
            sound_name=self._sound_name,
        )

    async def play(self, sound_name: str, fade_ms: int = 300):
        if sound_name not in self._sounds:
            raise ValueError("Sound not found: %s" % (sound_name))
        sound = self._sounds[sound_name]
        self._channel.set_volume(self._volume)
        self._channel.play(sound, fade_ms=fade_ms)
        self._sound_name = sound_name

    async def fadeout(self, fade_ms: int = 300):
        self._channel.fadeout(fade_ms)
        self._sound_name = None

    async def volume_sweep(
        self, volume_from: float, volume_to: float, time_ms: int = 300
    ):
        steps: int = min(time_ms // 50, 100)
        delta = (volume_to - volume_from) / steps
        for i in range(steps):
            volume = volume_from + (i + 1) * delta
            self._channel.set_volume(self._volume * volume)
            await asyncio.sleep(1e-3 * time_ms / steps)


class SoundSystem:
    def __init__(self, config, settings, update_cb):
        self._config: Config = config
        self._settings: Settings = settings
        self._update_cb: Callable[[SoundSystemState], None] = update_cb
        self._loop = asyncio.get_running_loop()

        # Init
        pygame.mixer.init()
        pygame.mixer.set_num_channels(4)
        pygame.mixer.set_reserved(2)

        self._sounds = load_sounds(os.path.join(self._config.data_dir, "sounds"))
        self._channels: dict[str, SoundChannel] = {
            name: SoundChannel(
                pygame.mixer.Channel(i),
                self._sounds,
                settings.subsettings(name),
            )
            for i, name in enumerate([MAIN_CH, EFFECT_CH])
        }

    async def open(self):
        _LOGGER.info("open")
        for ch in self._channels.values():
            ch.open()

    async def close(self):
        _LOGGER.info("close")
        pygame.mixer.quit()

    async def set_state(self, state: SoundSystemStateIn):
        _LOGGER.info("set state: %s" % (state))
        for name, ch_state in state.channels.items():
            if name not in self._channels:
                _LOGGER.warning("unknown sound channel: %s" % (name))
                continue
            await self._channels[name].set_state(ch_state)
        self._loop.call_soon(self._update_cb, self.get_state())

    def get_state(self) -> SoundSystemState:
        return SoundSystemState(
            channels={name: ch.get_state() for name, ch in self._channels.items()},
        )

    def get_info(self) -> SoundSystemInfo:
        sounds_state: dict[str, SoundInfo] = {}
        for name, sound in self._sounds.items():
            sounds_state[name] = SoundInfo(
                duration_secs=sound.get_length(),
            )
        return SoundSystemInfo(
            sounds=sounds_state,
        )

    async def maintain(self):
        while True:
            # _LOGGER.debug("busy: %d, channels: %d" % (
            #     pygame.mixer.get_busy(),
            #     pygame.mixer.get_num_channels()
            # ))
            await asyncio.sleep(2.0)

    async def play(self, channel: str, sound_name: str, **kwargs):
        _LOGGER.info("play (%s): %s, %s" % (channel, sound_name, kwargs))
        await self._channels[channel].play(sound_name, **kwargs)
        self._loop.call_soon(self._update_cb, self.get_state())

    async def fadeout(self, channel: str, **kwargs):
        _LOGGER.info("fadeout (%s): %s" % (channel, kwargs))
        await self._channels[channel].fadeout(**kwargs)
        self._loop.call_soon(self._update_cb, self.get_state())

    async def volume_sweep(
        self, channel: str, volume_from: float, volume_to: float, **kwargs
    ):
        _LOGGER.info(
            "volume sweep (%s): %.2f -> %.2f (%s)"
            % (channel, volume_from, volume_to, kwargs)
        )
        await self._channels[channel].volume_sweep(volume_from, volume_to, **kwargs)


def load_sounds(sounds_dir: str, suffix: str = ".wav") -> dict[str, pygame.mixer.Sound]:
    _LOGGER.info("load sounds... (dir: %s)" % (sounds_dir))
    start_time = time.time()

    res = {}
    for fname in os.listdir(sounds_dir):
        if not fname.endswith(suffix):
            _LOGGER.warning("unknown sound file: %s" % (fname))
            continue
        _LOGGER.info("loading sound file: %s" % (fname))
        sound_file_path = os.path.join(sounds_dir, fname)
        name = fname[: -len(suffix)]
        sound = pygame.mixer.Sound(sound_file_path)
        res[name] = sound
    _LOGGER.info("load sounds done in: %.3f s" % (time.time() - start_time))
    return res
