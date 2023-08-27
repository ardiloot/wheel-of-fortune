import os
import asyncio
import logging
import pygame
from typing import Callable
from ._config import Config
from ._settings import Settings
from .schemas import (
    SoundChannelState,
    SoundChannelStateIn,
    SoundState,
    SoundSystemState,
    SoundSystemStateIn,
)

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "SoundSystem",
]


class SoundChannel:

    def __init__(self, name, channel, sounds, settings):
        self.name: str = name
        self._channel: pygame.mixer.Channel = channel
        self._sounds: dict[str, pygame.mixer.Sound] = sounds
        self._settings: Settings = settings

        self._volume: float = 0.1
        self._sound_name: str | None = None

    def open(self):
        if "volume" in self._settings:
            self._volume = self._settings["volume"]

    async def set_state(self, state: SoundChannelStateIn):
        if state.volume is not None:
            self._channel.set_volume(self._volume)
            self._volume = state.volume
            self._settings["volume"] = self._volume
        
        if state.sound_name is not None:
            await self.play(state.sound_name)

    def get_state(self) -> SoundChannelState:
        return SoundChannelState(
            volume=self._volume,
            sound_name=self._sound_name,
        )

    async def play(self, sound_name: str, fade_ms: int = 300):
        _LOGGER.info("play (%s): %s" % (self.name, sound_name))
        if sound_name not in self._sounds:
            raise ValueError("Sound not found: %s" % (sound_name))
        
        sound = self._sounds[sound_name]
        self._channel.play(sound, fade_ms=fade_ms)  # TODO: loops, maxtime
        self._channel.set_volume(self._volume)  # Reset with every play command
        self._sound_name = sound_name
        
    async def fadeout(self, fade_ms: int = 300):
        _LOGGER.info("fadeout (%s): %d ms" % (self.name, fade_ms))
        self._channel.fadeout(fade_ms)
        self._sound_name = None

    async def volume_sweep(self, volume_from: float, volume_to: float, time_ms: int = 300):
        _LOGGER.info("volume sweep (%s): %.2f -> %.2f in %d ms" % (self.name, volume_from, volume_to, time_ms))
        steps: int = min(time_ms // 50, 100)
        delta = (volume_to - volume_from) / steps
        for i in range(steps):
            volume = volume_from + (i + 1) * delta
            self._channel.set_volume(volume)
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

        # Load sounds
        self._sounds = load_sounds(os.path.join(config.data_dir, "sounds"))

        # Channels
        self.main_ch = SoundChannel(
            "main",
            pygame.mixer.Channel(0),
            self._sounds,
            settings.subsettings("main"),
        )

        self.effect_ch = SoundChannel(
            "effect",
            pygame.mixer.Channel(1),
            self._sounds,
            settings.subsettings("effect"),
        )
        
        self._channels = {ch.name: ch for ch in [
            self.main_ch,
            self.effect_ch,
        ]}

    async def open(self):
        _LOGGER.info("open")
        for ch in self._channels.values():
            ch.open()

    async def close(self):
        _LOGGER.info("close")
        pygame.mixer.quit()

    async def set_state(self, state: SoundSystemStateIn):
        if state.main_ch is not None:
            await self.main_ch.set_state(state.main_ch)
        if state.effect_ch is not None:
            await self.effect_ch.set_state(state.effect_ch)
        self._loop.call_soon(self._update_cb, self.get_state())
        
    def get_state(self) -> SoundSystemState:
        sounds_state: dict[str, SoundState] = {}
        for name, sound in self._sounds.items():
            sounds_state[name] = SoundState(
                volume=sound.get_volume(),
                duration_secs=sound.get_length(),
            )

        return SoundSystemState(
            main_ch=self.main_ch.get_state(),
            effect_ch=self.effect_ch.get_state(),
            sounds=sounds_state,
        )
        
    async def maintain(self):
        while True:
            # _LOGGER.debug("busy: %d, channels: %d" % (
            #     pygame.mixer.get_busy(),
            #     pygame.mixer.get_num_channels()
            # ))
            await asyncio.sleep(2.0)


def load_sounds(sounds_dir: str, suffix: str = ".mp3") -> dict[str, pygame.mixer.Sound]:
    _LOGGER.info("load sounds... (dir: %s)" % (sounds_dir))
    res = {}
    for fname in os.listdir(sounds_dir):
        if not fname.endswith(suffix):
            _LOGGER.warn("unknown sound file: %s" % (fname))
            continue
        _LOGGER.info("loading sound file: %s" % (fname))

        sound = pygame.mixer.Sound(os.path.join(sounds_dir, fname))
        name = fname[:-len(suffix)]
        res[name] = sound
    _LOGGER.info("load sounds done.")
    return res
