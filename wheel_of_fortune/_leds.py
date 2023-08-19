import asyncio
import aiohttp
import logging
from ._config import Config
from ._settings import Settings


_LOGGER = logging.getLogger(__name__)


PALLETE_MAP = {
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
        self.set_state()

    def set_state(self,
        enabled=True,
        brightness=1.0,
        pallete="default",
        primary_color="#FF0000",
        secondary_color="#000000",
        effect="solid",
        effect_speed=0.5,
        effect_intensity=0.5
    ):
        if enabled is not None:
            self._enabled = enabled
        if brightness is not None:
            self._brightness = brightness
        if pallete is not None:
            self._pallete = pallete
        if primary_color is not None:
            self._primary_color = primary_color
        if secondary_color is not None:
            self._secondary_color = secondary_color
        if effect is not None:
            self._effect = effect
        if effect_speed is not None:
            self._effect_speed = effect_speed
        if effect_intensity is not None:
            self._effect_intensity = effect_intensity

    def get_state(self):
        return {
            "enabled": self._enabled,
            "brightness": self._brightness,
            "pallete": self._pallete,
            "primary_color": self._primary_color,
            "secondary_color": self._secondary_color,
            "effect": self._effect,
            "effect_speed": self._effect_speed,
            "effect_intensity": self._effect_intensity,
        }

    def compile_state(self):

        def to_rgb(h):
            return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

        def normalize(v):
            return int(max(0, min(255, round(255 * v))))

        pallete_id = PALLETE_MAP[self._pallete]
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
            
            "pal": pallete_id,                  # pallete id
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
    
    @property
    def enabled(self):
        return self._enabled


class LedController:

    def __init__(self, config, settings):
        self._config: Config = config
        self._settings: Settings = settings
        self._brightness = 0.5
        self._segments = {}
        for segment in config.wled_segments:
            self._segments[segment.name] = LedSegment(segment.start, segment.stop)

    async def open(self):
        _LOGGER.info("open")
        self._session = aiohttp.ClientSession(
            base_url=self._config.wled_url,
            raise_for_status=True,
        )
        if "brightness" in self._settings:
            self._brightness = self._settings["brightness"]
            
    async def close(self):
        _LOGGER.info("close")
        await self._session.close()
        _LOGGER.info("close done.")
    
    async def set_state(self, brightness=None, segments=None):
        _LOGGER.info("set_state: %s %s" % (brightness, segments))
        if brightness is not None:
            self._brightness = brightness
            self._settings.set("brightness", brightness)

        if segments is not None:
            for name, segment in self._segments.items():
                params = segments.get(name, {"enabled": False})
                segment.set_state(**params)
        await self._sync_state(sync_segments=segments is not None)

    async def get_state(self):
        return {
            "power_on": self._brightness > 0.0,
            "brightness": self._brightness,
            "segments": dict((name, segment.get_state()) for name, segment in self._segments.items())
        }

    async def maintain(self):
        while True:
            resp = await self._session.get("/json/state")
            state = await resp.json()
            _LOGGER.info("led state: %s" % (state))
            await asyncio.sleep(100.0)
            
    async def _sync_state(self, sync_segments=True):
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

        print("sync_state", state)
        await self._session.post("/json/state", json=state)
