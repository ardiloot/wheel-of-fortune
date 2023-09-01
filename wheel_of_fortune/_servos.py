import asyncio
import aiohttp
import logging
from typing import Callable
from ._config import Config
from .schemas import (
    ServoState,
    ServoStateIn,
    ServoInfo,
    ServosState,
    ServosStateIn,
    ServosInfo,
)

_LOGGER = logging.getLogger(__name__)


class ServoMotor:
    def __init__(self, pwm_id, mount_angle, zero_duty, full_duty, mount_duty):
        self.pwm_id = pwm_id
        self._mount_angle = mount_angle
        self._zero_duty = zero_duty
        self._full_duty = full_duty
        self._mount_duty = mount_duty

        self._pos = 0.0
        self._detached = True

    def set_state(self, state: ServoStateIn):
        if state.pos is not None:
            self._pos = state.pos
        if state.detached is not None:
            self._detached = state.detached

    def get_state(self) -> ServoState:
        return ServoState(
            pos=self._pos,
            duty=self.get_duty(),
            detached=self._detached,
        )

    def get_info(self) -> ServoInfo:
        return ServoInfo(
            mount_angle=self._mount_angle,
            zero_duty=self._zero_duty,
            full_duty=self._full_duty,
            mount_duty=self._mount_duty,
        )

    def get_duty(self):
        if self._detached:
            return 0.0
        return self._pos_to_duty(self._pos)

    def _pos_to_duty(self, pos: float | None) -> float:
        if pos is None:
            return 0.0
        return pos * (self._full_duty - self._zero_duty) + self._zero_duty

    def _duty_to_pos(self, duty: float) -> float | None:
        if duty == 0.0:
            return None
        return (duty - self._zero_duty) / (self._full_duty - self._zero_duty)


class ServoController:
    def __init__(self, config, update_cb):
        self._config: Config = config
        self._update_cb: Callable[[ServosState], None] = update_cb
        self._loop = asyncio.get_running_loop()
        self._session: aiohttp.ClientSession | None = None
        self._info = {}

        self._motors = {}
        for i, servo_conf in enumerate(config.servos):
            pwm_id = "%d" % (i)
            self._motors[servo_conf.name] = ServoMotor(
                pwm_id,
                servo_conf.mount_angle,
                self._config.servo_zero_duty,
                self._config.servo_full_duty,
                self._config.servo_mount_duty,
            )

    async def open(self):
        _LOGGER.info("open")
        self._session = aiohttp.ClientSession(
            base_url=self._config.wled_url,  # type: ignore
            raise_for_status=True,  # type: ignore
        )
        resp = await self._session.get("/json/info")
        self._info = await resp.json()
        _LOGGER.debug("info: %s" % (self._info))

    async def close(self):
        if self._session is None:
            return
        _LOGGER.info("close")
        await self._session.close()
        _LOGGER.info("close done.")

    async def set_state(self, state: ServosStateIn):
        _LOGGER.info("set_state: %s" % (state))
        for name, motor in self._motors.items():
            if name in state.motors:
                motor.set_state(state.motors[name])
        await self._sync_state()

    def get_state(self) -> ServosState:
        return ServosState(
            motors={name: motor.get_state() for name, motor in self._motors.items()}
        )

    def get_info(self) -> ServosInfo:
        return ServosInfo(
            version=self._info.get("ver", ""),
            motors={name: motor.get_info() for name, motor in self._motors.items()},
        )

    async def maintain(self):
        while True:
            # state = self.get_state()
            # _LOGGER.info("servos state: %s" % (state))
            await asyncio.sleep(100.0)

    async def move_to_pos(
        self, names: list[str], target_pos: float, duration_secs: float = 3.0
    ):
        _LOGGER.info(
            "move to pos: %s, target: %.3f, duration %.3f s"
            % (names, target_pos, duration_secs)
        )
        if len(names) == 0:
            return

        selected_motors = {}
        start_positions = {}
        for name in names:
            if name not in self._motors:
                _LOGGER.warn("unknown servo name: %s" % (name))
                continue
            motor = self._motors[name]
            selected_motors[name] = motor
            start_positions[name] = motor.get_state().pos

        step_rate_hz = 10.0
        steps = max(1, int(step_rate_hz * duration_secs))
        for i in range(steps):
            t0 = self._loop.time()
            for name, motor in selected_motors.items():
                motor_step = (target_pos - start_positions[name]) / steps
                next_pos = start_positions[name] + (i + 1) * motor_step
                motor.set_state(ServoStateIn(pos=next_pos, detached=False))
            await self._sync_state()
            t1 = self._loop.time()

            sleep_dur = max(0.0, duration_secs / steps - (t1 - t0))
            _LOGGER.debug(
                "step: %d, sync: %.3f s, sleep: %.3f s" % (i, (t1 - t0), sleep_dur)
            )
            await asyncio.sleep(sleep_dur)

    async def _sync_state(self):
        _LOGGER.info("sync state")
        if self._session is None:
            raise ConnectionError("Session is not opened")

        pwm_data = {}
        for motor in self._motors.values():
            pwm_data[motor.pwm_id] = {"duty": motor.get_duty()}

        await self._session.post("/json/state", json={"pwm": pwm_data})
        self._loop.call_soon(self._update_cb, self.get_state())
