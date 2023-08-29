import os
import asyncio
import logging
import importlib.metadata
from enum import Enum
from typing import Callable
from ._config import Config
from ._settings import SettingsManager, Settings
from ._encoder import Encoder
from ._leds import LedController
from ._servos import ServoController
from ._soundsystem import SoundSystem, MAIN_CH, EFFECT_CH
from ._telemetry import Telemetry, Point
from ._themes import load_themes, Theme
from ._effects import load_effects, Effect
from .schemas import (
    EncoderState,
    LedsState,
    LedsStateIn,
    ServosState,
    SoundSystemState,
    ServosStateIn,
    SectorState,
    SectorStateIn,
    WheelState,
    WheelStateIn,
    WheelInfo,
    WheelStateUpdate,
)

_LOGGER = logging.getLogger(__name__)
VERSION = importlib.metadata.version("wheel_of_fortune")

__all__ = [
    "Wheel",
]


class TaskType(Enum):
    STARTUP = "startup"
    IDLE = "idle"
    SPINNING = "spinning"
    STOPPED = "stopped"
    POWEROFF = "poweroff"
    UNKNOWN = "unknown"


class Sector:

    def __init__(self, index, settings, effects):
        self.index: int = index
        self._settings: Settings = settings
        self._effects: dict[str, Effect] = effects
        self.name: str = "sector %d" % (index)
        self.effect_id: str = list(effects.keys())[0]

    def init(self):
        if "name" in self._settings:
            self.name = self._settings["name"]
        if "effect_id" in self._settings:
            self.effect_id = self._settings["effect_id"]

    def set_state(self, state: SectorStateIn):
        if state.name is not None:
            _LOGGER.info("Set sector %d name: %s -> %s" % (self.index, self.name, state.name))
            self.name = state.name
            self._settings.set("name", self.name)
        if state.effect_id is not None:
            _LOGGER.info("Set sector %d effect: %s -> %s" % (self.index, self.effect_id, state.effect_id))
            if state.effect_id not in self._effects:
                raise ValueError("unknown effect id")
            self.effect_id = state.effect_id
            self._settings.set("effect", self.effect_id)
    
    def get_state(self) -> SectorState:
        return SectorState(
            index=self.index,
            name=self.name,
            effect_id=self.effect_id,
        )

    @property
    def effect(self):
        return self._effects[self.effect_id]


class Wheel:
    
    def __init__(self, config, gpio):
        self._config: Config = config
        self._loop = asyncio.get_running_loop()
        self._gpio = gpio
        self._subscriptions: list[Callable[[WheelStateUpdate], None]] = []

        self._poweroff_pin = "PL8"
        self._gpio.setup(self._poweroff_pin, self._gpio.IN, pull_up_down=self._gpio.PUD_OFF)

        settings_file = os.path.join(self._config.data_dir, "settings.json")
        self._settings_mgr = SettingsManager(settings_file)
        self._settings = self._settings_mgr["wheel"]

        self._telemetry = Telemetry(config)
        self._encoder = Encoder(config, self._gpio, self._telemetry, self._encoder_update)
        self._leds = LedController(config, self._settings_mgr["leds"], self._leds_update)
        self._servos = ServoController(config, self._servos_update)
        self._soundsystem = SoundSystem(config, self._settings_mgr["sound"], self._soundsystem_update)

        self._active_task: asyncio.Task | None = None
        self._next_task: TaskType = TaskType.STARTUP

        themes_file = os.path.join(config.data_dir, "themes.yaml")
        self._themes = load_themes(themes_file)
        self._theme_id: str = list(self._themes.keys())[0]

        effects_file = os.path.join(config.data_dir, "effects.yaml")
        self._effects = load_effects(effects_file)

        self._sectors: list[Sector] = []
        for i in range(config.num_sectors):
            sector_settings = self._settings.subsettings("sectors").subsettings("%d" % (i))
            self._sectors.append(Sector(i, sector_settings, self._effects))

    async def init(self):
        _LOGGER.info("init")

        # Open settings
        await self._settings_mgr.open()
        if "theme_id" in self._settings:
            theme_id = self._settings["theme_id"]
            if theme_id in self._themes:
                self._theme_id = theme_id
            else:
                _LOGGER.warn("unknown theme id: %s" % (theme_id))

        for sector in self._sectors:
            sector.init()

        # Open connections
        await asyncio.gather(
            self._telemetry.open(),
            self._encoder.open(),
            self._leds.open(),
            self._servos.open(),
            self._soundsystem.open(),
        )

    async def close(self):
        _LOGGER.info("close")
        await asyncio.gather(
            self._settings_mgr.close(),
            self._telemetry.close(),
            self._leds.close(),
            self._servos.close(),
            self._encoder.close(),
            self._soundsystem.close(),
        )
        if self._active_task is not None and not self._active_task.done():
            self._active_task.cancel()

    async def set_state(self, state: WheelStateIn):

        if state.theme_id is not None:
            _LOGGER.info("activate_theme: %s" % (state.theme_id))
            if state.theme_id in self._themes:
                self._theme_id = state.theme_id
            else:
                raise ValueError("unknown theme name")
            self._settings.set("theme", self._theme_id)
            self._publish_update(WheelStateUpdate(
                theme_id=self._theme_id,
            ))

        if len(state.sectors) > 0:
            for index, sector_state in state.sectors.items():
                if index < 0 or index >= len(self._sectors):
                    raise ValueError("Sector index out of bounds")
                sector = self._sectors[index]
                sector.set_state(sector_state)
            
            self._publish_update(WheelStateUpdate(
                sectors=[sector.get_state() for sector in self._sectors]
            ))

        if state.servos:
            await self._servos.set_state(state.servos)

        if state.leds:
            await self._leds.set_state(state.leds)

        if state.soundsystem:
            await self._soundsystem.set_state(state.soundsystem)

    def get_state(self) -> WheelState:
        
        return WheelState(
            active_task=self._cur_task.value,
            theme_id=self._theme_id,
            sectors=[sector.get_state() for sector in self._sectors],
            encoder=self._encoder.get_state(),
            servos=self._servos.get_state(),
            leds=self._leds.get_state(),
            soundsystem=self._soundsystem.get_state(),
        )

    def get_info(self) -> WheelInfo:
        return WheelInfo(
            version=VERSION,
            themes={id: theme.get_info() for id, theme in self._themes.items()},
            effects={id: effect.get_info() for id, effect in self._effects.items()},
            leds=self._leds.get_info(),
            soundsystem=self._soundsystem.get_info(),
        )

    def subscribe(self, callback: Callable[[WheelStateUpdate], None]):
        self._subscriptions.append(callback)

    async def maintain(self):
        _LOGGER.info("maintain...")
        await asyncio.gather(
            self._settings_mgr.maintain(),
            self._encoder.maintain(),
            self._telemetry.maintain(),
            self._leds.maintain(),
            self._servos.maintain(),
            self._soundsystem.maintain(),
            self._maintain(),
            self._maintain_power_state(),
        )
        _LOGGER.info("maintain finished.")

    async def _maintain_power_state(self):
        _LOGGER.info("start maintaining power state")
        while True:
            if self._gpio.input(self._poweroff_pin):
                _LOGGER.info("poweroff requested...")
                self._schedule_task(TaskType.POWEROFF)

            await asyncio.sleep(1.0)

    async def _maintain(self):
        _LOGGER.info("start maintaining")
        self._next_task = TaskType.STARTUP

        while True:
            # Start next task
            task = self._next_task
            self._next_task = TaskType.IDLE
            task_co = {
                TaskType.STARTUP: self._task_startup,
                TaskType.IDLE: self._task_idle,
                TaskType.SPINNING: self._task_spinning,
                TaskType.STOPPED: self._task_stopped,
                TaskType.POWEROFF: self._task_poweroff,
            }[task]()
            _LOGGER.info("start task: %s" % (task))
            active_task_name = task.value
            self._active_task = asyncio.create_task(task_co, name=active_task_name)
            self._publish_update(WheelStateUpdate(
                active_task=active_task_name,
            ))

            # Wait for task
            try:
                await self._active_task
            except asyncio.CancelledError:
                _LOGGER.info("task was cancelled: %s" % (self._cur_task))
                pass
            _LOGGER.info("task finished: %s" % (self._cur_task))

    def _schedule_task(self, task: TaskType):
        if task == self._cur_task:
            return
        
        if self._cur_task == TaskType.POWEROFF:
            _LOGGER.warn("Cannot schedule tasks after poweroff")
            return

        _LOGGER.info("_schedule_task %s -> %s:" % (self._cur_task, task))
        self._next_task = task
        if self._active_task is not None and not self._active_task.done():
            success = self._active_task.cancel()
            if not success:
                raise RuntimeError("ERROR cancelling task")
            
    def _reload_task(self):
        _LOGGER.info("reload task")
        if self._active_task is not None and not self._active_task.done():
            success = self._active_task.cancel()
            if not success:
                raise RuntimeError("ERROR cancelling task")

    async def _task_startup(self):
        await self._leds.set_state(LedsStateIn(segments=self._theme.startup_led_preset))
        await asyncio.sleep(2)

    async def _task_idle(self):
        cur_theme = None
        counter = 0
        while True:
            if cur_theme is None or cur_theme != self._theme:
                await self._leds.set_state(LedsStateIn(segments=self._theme.idle_led_preset))
                cur_theme = self._theme
            await asyncio.sleep(1.0)
            counter += 1
            if counter % 15 == 0:
                _LOGGER.info("idle heartbeat")

    async def _task_spinning(self):
        enc_state = self._encoder.get_state()
        start_sector = enc_state.sector
        start_sector_count = enc_state.total_sectors
        start_time = self._loop.time()
        try:
            await self._soundsystem.fadeout(MAIN_CH)
            await self._leds.set_state(LedsStateIn(segments=self._theme.spinning_led_preset))
            await self._soundsystem.play(MAIN_CH, self._theme.theme_sound)
            while True:
                await asyncio.sleep(1.0)
        finally:
            end_sector = enc_state.sector
            end_sector_count = enc_state.total_sectors
            end_time = self._loop.time()
            duration = end_time - start_time
            total_sectors = end_sector_count - start_sector_count
            avg_rpm = total_sectors / self._config.num_sectors / duration * 60.0

            _LOGGER.info("Spin: sector: %d -> %d, total_sectors: %d -> %d (%d), duration %.1fs, avg_rpm: %.2f" % (
                start_sector,
                end_sector,
                start_sector_count,
                end_sector_count,
                total_sectors,
                duration,
                avg_rpm
            ))

            point = Point("spin") \
                .field("start_sector", start_sector) \
                .field("end_sector", end_sector) \
                .field("start_sector_count", start_sector_count) \
                .field("total_sectors", total_sectors) \
                .field("duration", duration) \
                .field("avg_rpm", avg_rpm)
            self._telemetry.report_point(point)

    async def _task_stopped(self):
        try:
            enc_state = self._encoder.get_state()
            effect = self._sectors[enc_state.sector].effect

            await self._servos.set_state(ServosStateIn.model_validate({"motors": {"bottom": {"pos": 1.0}}}))
            await asyncio.sleep(1.0)

            await self._soundsystem.volume_sweep(MAIN_CH, 1.0, 0.2)
            await asyncio.sleep(0.2)

            await self._leds.set_state(LedsStateIn(segments=effect.leds_preset))
            await self._soundsystem.play(EFFECT_CH, effect.effect_sound)
            await asyncio.sleep(2.0)

            await self._soundsystem.volume_sweep(MAIN_CH, 0.2, 1.0, time_ms=1000)
            await asyncio.sleep(4.0)

            await self._servos.set_state(ServosStateIn.model_validate({"motors": {"bottom": {"pos": 0.0}}}))
            await asyncio.sleep(3.0)
            await self._soundsystem.fadeout(MAIN_CH, fade_ms=2000)

        finally:
            await self._soundsystem.fadeout(MAIN_CH)
            await self._servos.set_state(ServosStateIn.model_validate({"motors": {"bottom": {"pos": 0.0}}}))

    async def _task_poweroff(self):
        await self._soundsystem.fadeout(MAIN_CH)
        await self._leds.set_state(LedsStateIn(segments=self._theme.poweroff_led_preset))
        while True:
            await asyncio.sleep(5.0)

    async def __aenter__(self):
        await self.init()
        return self

    async def __aexit__(self, *args):
        await self.close()

    @property
    def _cur_task(self):
        if self._active_task is None:
            return TaskType.UNKNOWN
        return TaskType(self._active_task.get_name())
    
    @property
    def _theme(self) -> Theme:
        return self._themes[self._theme_id]

    def _encoder_update(self, state: EncoderState):
        _LOGGER.debug("encoder update: %s" % (state))
        if state.standstill:
            self._schedule_task(TaskType.STOPPED)
        else:
            self._schedule_task(TaskType.SPINNING)
            
        self._publish_update(WheelStateUpdate(
            encoder=state,
        ))

    def _leds_update(self, state: LedsState):
        self._publish_update(WheelStateUpdate(
            leds=state,
        ))

    def _servos_update(self, state: ServosState):
        self._publish_update(WheelStateUpdate(
            servos=state,
        ))

    def _soundsystem_update(self, state: SoundSystemState):
        self._publish_update(WheelStateUpdate(
            soundsystem=state,
        ))

    def _publish_update(self, update: WheelStateUpdate):
        for callback in self._subscriptions:
            self._loop.call_soon(callback, update)

    @property
    def encoder(self):
        return self._encoder

    @property
    def servos(self):
        return self._servos

    @property
    def leds(self):
        return self._leds
    
    @property
    def sound(self):
        return self._soundsystem
    
    @property
    def sectors(self):
        return self._sectors
    
