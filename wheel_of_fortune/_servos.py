import asyncio
import aiohttp
import logging
from ._config import Config
from .schemas import (
    ServoState,
    ServosState,
    ServoStateIn,
    ServosStateIn,
)

_LOGGER = logging.getLogger(__name__)


class ServoController:

    def __init__(self, config):
        self._config: Config = config
        self._session: aiohttp.ClientSession | None = None
        self._id_map = {
            "bottom": "0",
            "right": "1",
            "left": "2",
        }
        self._name_map = {v: k for k, v in self._id_map.items()}
        self._zero_duty = 0.087
        self._full_duty = 0.0516
        # self._mount_duty = 0.047352

    async def open(self):
        _LOGGER.info("open")
        self._session = aiohttp.ClientSession(
            base_url=self._config.wled_url,  # type: ignore
            raise_for_status=True,  # type: ignore
        )
            
    async def close(self):
        if self._session is None:
            return
        _LOGGER.info("close")
        await self._session.close()
        _LOGGER.info("close done.")

    async def set_state(self, state: ServosStateIn):
        if self._session is None:
            raise ConnectionError("Session is not opened")
        pwm_data = {}
        for name, pwm_id in self._id_map.items():
            if name in state.servos:
                s: ServoStateIn = state.servos[name]
                duty = self._pos_to_duty(s.pos) if not s.detached else None
                pwm_data[pwm_id] = {"duty": duty}
        await self._session.post("/json/state", json={"pwm": pwm_data})

    async def get_state(self) -> ServosState:
        _LOGGER.info("get_state")
        if self._session is None:
            raise ConnectionError("Session is not opened")
        
        resp = await self._session.get("/json/state")
        data = await resp.json()

        res_servos: dict[str, ServoState] = {}
        for _id, s in data.get("pwm", {}).items():
            duty = s.get("duty", 0.0)
            pos = self._duty_to_pos(duty)
            res_servos[self._name_map.get(_id, _id)] = ServoState(
                pos=pos,
                duty=duty,
                detached=duty == 0.0,
            )
        return ServosState(servos=res_servos)
    
    async def maintain(self):
        while True:
            state = await self.get_state()
            _LOGGER.info("servos state: %s" % (state))
            await asyncio.sleep(100.0)

    def _pos_to_duty(self, pos):
        if pos is None:
            return 0.0
        return pos * (self._full_duty - self._zero_duty) + self._zero_duty

    def _duty_to_pos(self, duty):
        if duty == 0.0:
            return None
        return (duty - self._zero_duty) / (self._full_duty - self._zero_duty)
