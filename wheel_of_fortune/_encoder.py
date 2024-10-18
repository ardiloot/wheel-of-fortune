import asyncio
import logging
from typing import Callable
from ._config import Config
from ._utils import AsyncTimer, decode_grey_code, encode_gray_code
from ._telemetry import Telemetry, Point
from .schemas import EncoderState

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Encoder",
]


class Encoder:
    def __init__(self, config, gpio, telemetry, update_cb):
        self._config: Config = config
        self._gpio = gpio
        self._telemetry: Telemetry = telemetry
        self._update_cb: Callable[[EncoderState], None] = update_cb

        self._loop = asyncio.get_running_loop()

        self._encoder_pins: list[str] = ["PH3", "PH4", "PH6", "PH5"]
        self._speed_pin: str = "PL10"
        self._pulses_per_rev: float = 128.0
        self._standstill_timeout = 1.0

        self._encoder_state: list[bool] = []
        self._total_sector_count: int = 0
        self._missed_sector_count: int = 0

        self._speed_pulse_count: int = 0
        self._last_speed_pulse_count: int = 0
        self._rpm: float = 0.0
        self._last_rpm_update: float = self._loop.time()

        # Position interrupt
        for pin in self._encoder_pins:
            self._gpio.setup(pin, self._gpio.IN, pull_up_down=self._gpio.PUD_OFF)
            self._gpio.add_event_detect(
                pin, self._gpio.BOTH, callback=self._int_pos_callback
            )
            self._encoder_state.append(self._gpio.input(pin))
        self._sector = self._decode_sector()

        # Speed interrupt
        self._gpio.setup(
            self._speed_pin, self._gpio.IN, pull_up_down=self._gpio.PUD_OFF
        )
        self._gpio.add_event_detect(
            self._speed_pin, self._gpio.BOTH, callback=self._int_speed_callback
        )

        # Standstill timer
        self._is_standstill = True
        self._standstill_timer = AsyncTimer(
            self._standstill_timeout, self._standstill_detected
        )

    async def open(self):
        pass

    async def close(self):
        pass

    def get_state(self) -> EncoderState:
        return EncoderState(
            sector=self._sector,
            rpm=self._rpm,
            total_revs=self._speed_pulse_count / self._pulses_per_rev,
            total_sectors=self._total_sector_count,
            missed_sector_count=self._missed_sector_count,
            standstill=self._is_standstill,
        )

    async def maintain(self):
        counter = 0
        while True:
            now = self._loop.time()
            dpulses = self._speed_pulse_count - self._last_speed_pulse_count
            dtime = now - self._last_rpm_update
            self._rpm = dpulses / dtime / self._pulses_per_rev * 60.0
            self._last_speed_pulse_count = self._speed_pulse_count
            self._last_rpm_update = now

            log_cycles = 60 if self._is_standstill else 1
            if counter % log_cycles == 0:
                state = self.get_state()
                _LOGGER.info(
                    "sector: %d, rpm %.1f (%d pulses in %.1f ms), total_revs: %.1f, missed_sectors: %d"
                    % (
                        state.sector,
                        state.rpm,
                        dpulses,
                        1e3 * dtime,
                        state.total_revs,
                        state.missed_sector_count,
                    )
                )

            report_cycles = 10 if self._is_standstill else 1
            if counter % report_cycles == 0:
                state = self.get_state()
                point = (
                    Point("encoder")
                    .field("sector", state.sector)
                    .field("rpm", state.rpm)
                    .field("total_revs", state.total_revs)
                    .field("missed_sector_count", state.missed_sector_count)
                )
                self._telemetry.report_point(point)

            await asyncio.sleep(1.0)
            counter += 1

    async def test(self, initial_speed=20.0, drag_factor=0.1):
        _LOGGER.info(
            "starting test (initial speed: %.2f, drag_factor: %.2f)..."
            % (initial_speed, drag_factor)
        )
        # speed: [sectors per sec]
        # drag_factor: speed is reduced by drag_factor * speed for every sector
        cur_speed = initial_speed
        cur_sector = self._sector
        while abs(1.0 / cur_speed) < 1.0:
            # Update sector
            cur_sector = (cur_sector + 1) % self._config.num_sectors
            gray_code = encode_gray_code(cur_sector)
            for j in range(len(self._encoder_state) - 1, -1, -1):
                self._encoder_state[j] = gray_code % 2 != 0
                gray_code //= 2

            await asyncio.sleep(1.0 / cur_speed)
            self._encoder_update(self._loop.time())

            # Update speed
            cur_speed = cur_speed - drag_factor * cur_speed

            _LOGGER.info(
                "test %d -> %d, speed %.2f, time per sector: %.1f"
                % (cur_sector, self._sector, cur_speed, 1.0 / cur_speed)
            )
        _LOGGER.info("test finished.")

    def _standstill_detected(self):
        self._is_standstill = True
        self._update_cb(self.get_state())

    def _decode_sector(self):
        res = 0
        for value in self._encoder_state:
            res = 2 * res + value
        res = decode_grey_code(res)
        return res

    def _encoder_update(self, t):
        try:
            delay = self._loop.time() - t
            if delay > 10e-3:
                _LOGGER.warning("encoder_update delay %.3f ms" % (1e3 * delay))

            self._speed_pulse_count += 1
            old_sector = self._sector
            new_sector = self._decode_sector()
            if old_sector == new_sector:
                return

            self._total_sector_count += 1
            n = self._config.num_sectors
            if (old_sector + 1) % n != new_sector and (
                old_sector - 1 + n
            ) % n != new_sector:
                _LOGGER.warning(
                    "WARN: skipped sector %d -> %d" % (old_sector, new_sector)
                )
                self._missed_sector_count += 1

            self._sector = new_sector
            self._is_standstill = False
            self._standstill_timer.start()
            self._update_cb(self.get_state())
        except Exception:
            _LOGGER.exception("error in encoder update")

    def _int_pos_callback(self, pin):
        # Called by OPi.GPIO thread
        value = self._gpio.input(pin)
        self._encoder_state[self._encoder_pins.index(pin)] = value

    def _int_speed_callback(self, pin):
        # Called by OPi.GPIO thread
        self._loop.call_soon_threadsafe(self._encoder_update, self._loop.time())
