import asyncio
import aiohttp
import logging
from ._config import Config


_LOGGER = logging.getLogger(__name__)


class ServoController:

    def __init__(self, config):
        self._config: Config = config

    async def open(self):
        _LOGGER.info("open")
        self._id_map = {
            "bottom": "0",
            "right": "1",
            "left": "2",
        }
        self._name_map = {v: k for k, v in self._id_map.items()}
        self._idle_duty = 0.087
        self._erect_duty = 0.0516
        # self._mount_duty = 0.047352
        self._session = aiohttp.ClientSession(
            base_url=self._config.wled_url,
            raise_for_status=True,
        )
            
    async def close(self):
        _LOGGER.info("close")
        await self._session.close()
        _LOGGER.info("close done.")

    async def set_pos(self, pos, names=None):
        _LOGGER.info("set_servo_pos: %s %s" % (names, pos))
        duty = self._pos_to_duty(pos)

        pwm_data = {}
        for name in names or self._id_map.keys():
            if name not in self._id_map:
                continue
            pwm_data[self._id_map[name]] = {"duty": duty}
        
        await self._session.post("/json/state", json={"pwm": pwm_data})

    async def set_state(self, pos=None, detached=False, names=None):
        if detached:
            await self.set_pos(None, names=names)
        elif pos is not None:
            await self.set_pos(pos, names=names)

    async def get_state(self):
        _LOGGER.info("get_state")
        resp = await self._session.get("/json/state")
        data = await resp.json()

        res = {}
        for _id, s in data.get("pwm", {}).items():
            duty = s.get("duty", 0.0)
            pos = self._duty_to_pos(duty)
            res[self._name_map.get(_id, _id)] = {
                "pos": pos,
                "duty": duty,
                "detached": duty == 0.0,
            }
        return res

    async def _update_state(self, state):
        await self._session.post("/json/state", json=state)

    async def maintain(self):
        while True:
            state = await self.get_state()
            _LOGGER.info("servos state: %s" % (state))
            await asyncio.sleep(100.0)

    def _pos_to_duty(self, pos):
        if pos is None:
            return 0.0
        return pos * (self._erect_duty - self._idle_duty) + self._idle_duty

    def _duty_to_pos(self, duty):
        if duty == 0.0:
            return None
        return (duty - self._idle_duty) / (self._erect_duty - self._idle_duty)
