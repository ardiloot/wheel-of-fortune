import asyncio
import logging
from ._config import Config
from ._utils import AsyncTimer, decode_grey_code, encode_gray_code
from ._telemetry import Point

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Encoder",
]


class Encoder:

    def __init__(self, config, gpio, callback, telemetry):
        self._config: Config = config
        self._gpio = gpio
        self._callback = callback
        self._telemetry = telemetry
        self._loop = asyncio.get_running_loop()
        
        self._encoder_pins = ["PH3", "PH4", "PH6", "PH5"]
        self._speed_pin = "PL10"
        self._sectors_per_rev = self._config.num_sectors
        self._pulses_per_rev = 128.0

        self._encoder_state = []
        self._total_sector_count = 0
        self._missed_sector_count = 0

        self._speed_pulse_count = 0
        self._last_speed_pulse_count = 0
        self._rpm = 0.0
        self._last_rpm_update = self._loop.time()

        # Position interrupt
        for pin in self._encoder_pins:
            self._gpio.setup(pin, self._gpio.IN, pull_up_down=self._gpio.PUD_OFF)
            self._gpio.add_event_detect(pin, self._gpio.BOTH, callback=self._int_pos_callback)
            self._encoder_state.append(self._gpio.input(pin))
        self._sector = self._decode_sector()

        # Speed interrupt
        self._gpio.setup(self._speed_pin, self._gpio.IN, pull_up_down=self._gpio.PUD_OFF)
        self._gpio.add_event_detect(self._speed_pin, self._gpio.BOTH, callback=self._int_speed_callback)

        # Standstill timer
        self._is_standstill = True
        self._standstill_timer = AsyncTimer(3.5, self._standstill_detected)

    async def open(self):
        pass

    async def close(self):
        pass

    async def maintain(self):
        counter = 0
        while True:
            now = self._loop.time()
            dpulses = self._speed_pulse_count - self._last_speed_pulse_count
            dtime = now - self._last_rpm_update 
            self._rpm = dpulses / dtime / self._pulses_per_rev * 60.0
            self._last_speed_pulse_count = self._speed_pulse_count
            self._last_rpm_update = now
            
            report_cycles = 10 if self._is_standstill else 1
            if counter % report_cycles == 0:
                _LOGGER.debug("sector: %d, rpm %.1f (%d pulses in %.1f ms), total_revs: %.1f, missed_sectors: %d" % (
                    self.sector, self.rpm, dpulses, 1e3 * dtime, self.total_revs, self.missed_sector_count))

                point = Point("encoder") \
                    .field("sector", self.sector) \
                    .field("rpm", self.rpm) \
                    .field("total_revs", self.total_revs) \
                    .field("missed_sector_count", self.missed_sector_count)
                self._telemetry.report_point(point)
                
            await asyncio.sleep(1.0)
            counter += 1

    async def test(self, initial_speed=20.0, drag_factor=0.1):
        _LOGGER.info("starting test (initial speed: %.2f, drag_factor: %.2f)..." % (initial_speed, drag_factor))
        # speed: [sectors per sec]
        # drag_factor: speed is reduced by drag_factor * speed for every sector
        cur_speed = initial_speed
        cur_sector = self.sector
        while abs(1.0 / cur_speed) < 1.0:
            # Update sector
            cur_sector = (cur_sector + 1) % self._sectors_per_rev
            gray_code = encode_gray_code(cur_sector)
            for j in range(len(self._encoder_state) - 1, -1, -1):
                self._encoder_state[j] = gray_code % 2 != 0
                gray_code //= 2
            
            await asyncio.sleep(1.0 / cur_speed)
            self._encoder_update(self._loop.time())

            # Update speed
            cur_speed = cur_speed - drag_factor * cur_speed

            _LOGGER.info("test %d -> %d, speed %.2f, time per sector: %.1f" % (cur_sector, self.sector, cur_speed, 1.0 / cur_speed))
        _LOGGER.info("test finished.")

    def get_state(self):
        return dict(
            sector=self.sector,
            rpm=self.rpm,
            total_revs=self.total_revs,
            total_sectors=self.total_sectors,
            missed_sector_count=self.missed_sector_count,
            sectors_per_rev=self.sectors_per_rev,
            standstill=self.standstill
        )

    @property
    def sector(self):
        return self._sector

    @property
    def rpm(self):
        return self._rpm
    
    @property
    def total_revs(self):
        return self._speed_pulse_count / self._pulses_per_rev

    @property
    def total_sectors(self):
        return self._total_sector_count
    
    @property
    def missed_sector_count(self):
        return self._missed_sector_count

    @property
    def sectors_per_rev(self):
        return self._sectors_per_rev
    
    @property
    def standstill(self):
        return self._is_standstill

    def _standstill_detected(self):
        self._is_standstill = True
        self._callback("standstill", {"sector": self.sector})

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
                _LOGGER.warn("encoder_update delay %.3f ms" % (1e3 * delay))

            self._speed_pulse_count += 1
            old_sector = self._sector
            new_sector = self._decode_sector()
            if old_sector == new_sector:
                return

            self._total_sector_count += 1
            n = self._sectors_per_rev
            if (old_sector + 1) % n != new_sector and (old_sector - 1 + n) % n != new_sector:
                _LOGGER.warn("WARN: skipped sector %d -> %d" % (old_sector, new_sector))
                self._missed_sector_count += 1
            
            self._sector = new_sector
            self._is_standstill = False
            self._standstill_timer.start()
            self._callback("spinning", {"sector": new_sector})
        except Exception:
            _LOGGER.exception("error in encoder update")

    def _int_pos_callback(self, pin):
        # Called by OPi.GPIO thread
        value = self._gpio.input(pin)
        self._encoder_state[self._encoder_pins.index(pin)] = value

    def _int_speed_callback(self, pin):
        # Called by OPi.GPIO thread
        self._loop.call_soon_threadsafe(self._encoder_update, self._loop.time())
        
