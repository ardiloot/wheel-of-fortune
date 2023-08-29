import asyncio
import aiohttp
import logging
from typing import Callable
from ._config import Config
from ._settings import Settings
from .schemas import (
    LedSegmentState,
    LedSegmentStateIn,
    LedsState,
    LedsStateIn,
    LedsInfo,
)

_LOGGER = logging.getLogger(__name__)


PALETTE_MAP = {
    "default": 0,
    "color": 2,
    "rainbow": 11,
    "c9": 48,
}


EFFECT_MAP = {
    "solid": 0,
    "rainbow": 9,
    "sparkle": 20,
    "chase": 28,
}


class LedSegment:

    def __init__(self, start, stop):
        self._start = start
        self._stop = stop
        self.set_state(LedSegmentStateIn())

    def set_state(self, state: LedSegmentStateIn):
        if state.enabled is not None:
            self._enabled = state.enabled
        if state.brightness is not None:
            self._brightness = state.brightness
        if state.palette is not None:
            self._palette = state.palette
        if state.primary_color is not None:
            self._primary_color = state.primary_color
        if state.secondary_color is not None:
            self._secondary_color = state.secondary_color
        if state.effect is not None:
            self._effect = state.effect
        if state.effect_speed is not None:
            self._effect_speed = state.effect_speed
        if state.effect_intensity is not None:
            self._effect_intensity = state.effect_intensity

    def get_state(self) -> LedSegmentState:
        return LedSegmentState(
            enabled=self._enabled,
            brightness=self._brightness,
            palette=self._palette,
            primary_color=self._primary_color,
            secondary_color=self._secondary_color,
            effect=self._effect,
            effect_speed=self._effect_speed,
            effect_intensity=self._effect_intensity,
        )

    def compile_state(self) -> dict[str, int | float | str | list]:

        def to_rgb(h: str) -> tuple[int, int, int]:
            return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

        def normalize(v: float) -> int:
            return int(max(0, min(255, round(255 * v))))

        palette_id = PALETTE_MAP[self._palette]
        effect_id = EFFECT_MAP[self._effect]

        # https://kno.wled.ge/interfaces/json-api/
        return {
            
            "start": self._start,               # start led
            "stop": self._stop,                 # stop led
            "grp": 1,                           # grouping
            "spc": 0,                           # spacing
            "of": 0,                            # offset
            "rev": False,                       # flips the segment
            "mi": False,                        # mirrors the segment
            "on": self._enabled,                # on/off
            "bri": normalize(self._brightness), # brightness
            
            "pal": palette_id,                  # palette id
            "col": [
                to_rgb(self._primary_color),    # primary color
                to_rgb(self._secondary_color),  # secondary (bg) color
                [0, 0, 0],                      # tertiary color
            ],
            "cct": 127,                         # white spectrum color temperature
            
            "fx": effect_id,                    # effect id
            "sx": normalize(self._effect_speed),        # relative effect speed
            "ix": normalize(self._effect_intensity),    # effect intensity
            "c1": 128,                          # effect custom slider 1
            "c2": 128,                          # effect custom slider 2
            "c3": 16,                           # effect custom slider 3
            "o1": False,                        # effect option 1
            "o2": False,                        # effect option 2
            "o3": False,                        # effect option 3

            "sel": False,                       # selected
            "frz": False,                       # freeze
            "si": 0,                            # sound setting
            "m12": 2                            # expand 1d fx
        }
    

class LedController:

    def __init__(self, config, settings, update_cb):
        self._config: Config = config
        self._settings: Settings = settings
        self._update_cb: Callable[[LedsState], None] = update_cb
        self._loop = asyncio.get_running_loop()

        self._brightness: float = 0.5
        self._segments: dict[str, LedSegment] = {}

        for segment in config.wled_segments:
            self._segments[segment.name] = LedSegment(segment.start, segment.stop)
        
        self._session: aiohttp.ClientSession | None = None
        self._info = {}

    async def open(self):
        _LOGGER.info("open")
        self._session = aiohttp.ClientSession(
            base_url=self._config.wled_url,  # type: ignore
            raise_for_status=True,  # type: ignore
        )
        if "brightness" in self._settings:
            self._brightness = self._settings["brightness"]

        resp = await self._session.get("/json/info")
        self._info = await resp.json()
            
    async def close(self):
        if self._session is None:
            return
        _LOGGER.info("close")
        await self._session.close()
        _LOGGER.info("close done.")
    
    async def set_state(self, state: LedsStateIn):
        _LOGGER.info("set_state: %s %s" % (state.brightness, state.segments))
        if state.brightness is not None:
            self._brightness = state.brightness
            self._settings.set("brightness", state.brightness)

        if state.segments is not None:
            for name, segment in self._segments.items():
                params = state.segments.get(name, LedSegmentStateIn(enabled=False))
                segment.set_state(params)
        await self._sync_state(sync_segments=state.segments is not None)

    def get_state(self) -> LedsState:
        return LedsState(
            power_on=self._brightness > 0.0,
            brightness=self._brightness,
            segments=dict((name, segment.get_state()) for name, segment in self._segments.items()),
        )
    
    def get_info(self) -> LedsInfo:
        return LedsInfo(
            version=self._info.get("ver", "unknown"),
        )

    async def maintain(self):
        while True:
            if self._session:
                resp = await self._session.get("/json/state")
                state = await resp.json()
                _LOGGER.info("led state: %s" % (state))
            await asyncio.sleep(100.0)
            
    async def _sync_state(self, sync_segments=True):
        if self._session is None:
            raise ConnectionError("Session is not opened.")
        
        int_brightness = int(round(255 * self._brightness))
        state = {
            "on": int_brightness > 0,
            "bri": int_brightness,
            "transition": 0,
        }

        if sync_segments:
            segment_states = [s.compile_state() for s in self._segments.values()]
            for _ in range(len(segment_states), 32):
                segment_states.append({"stop": 0})
            state["seg"] = segment_states

        await self._session.post("/json/state", json=state)
        self._loop.call_soon(self._update_cb, self.get_state())
