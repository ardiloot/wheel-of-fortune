import os
import asyncio
import logging
from typing import Callable
from ._config import Config
from ._settings import SettingsManager, Settings
from ._encoder import Encoder
from ._leds import LedController
from ._servos import ServoController
from ._sound import Sound
from ._telemetry import Telemetry, Point
from ._themes import load_themes, Theme
from ._effects import load_effects, Effect
from .schemas import (
    LedsStateIn,
    ServosStateIn,
    ThemeState,
    EffectState,
    SectorState,
    SectorStateIn,
    WheelState,
    WheelStateIn,
    WheelStateUpdate,
)

_LOGGER = logging.getLogger(__name__)

__all__ = [
    "Wheel",
]


class Sector:

    def __init__(self, index, settings, effects):
        self.index: int = index
        self._settings: Settings = settings
        self._effects: dict[str, Effect] = effects
        self.name: str = "sector %d" % (index)
        self.effect: Effect = list(effects.values())[0]

    def init(self):
        if "name" in self._settings:
            self.name = self._settings["name"]
        if "effect" in self._settings:
            effect_id = self._settings["effect"]
            self.effect = self._effects[effect_id]

    def set_state(self, state: SectorStateIn):
        if state.name is not None:
            _LOGGER.info("Set sector %d name: %s -> %s" % (self.index, self.name, state.name))
            self.name = state.name
            self._settings.set("name", self.name)
        if state.effect is not None:
            _LOGGER.info("Set sector %d effect: %s -> %s" % (self.index, self.effect._id, state.effect))
            if state.effect not in self._effects:
                raise ValueError("unknown effect id")
            self.effect = self._effects[state.effect]
            self._settings.set("effect", state.effect)
    
    def get_state(self) -> SectorState:
        return SectorState(
            index=self.index,
            name=self.name,
            effect=self.effect._id,
        )


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
        self._encoder = Encoder(config, self._gpio, self._encoder_event, self._telemetry)
        self._leds = LedController(config, self._settings_mgr["leds"])
        self._servos = ServoController(config)
        self._sound = Sound(config, self._settings_mgr["sound"])

        self._active_task: asyncio.Task | None = None
        self._next_task_name: str = "startup"

        themes_file = os.path.join(config.data_dir, "themes.yaml")
        self._themes = load_themes(themes_file)
        self._theme: Theme = list(self._themes.values())[0]

        effects_file = os.path.join(config.data_dir, "effects.yaml")
        self._effects = load_effects(effects_file)

        self._sectors: list[Sector] = []
        for i in range(config.num_sectors):
            sector_settings = self._settings.subsettings("sectors").subsettings("%d" % (i))
            self._sectors.append(Sector(i, sector_settings, self._effects))
        
        self._theme_sound_channel = None

    async def init(self):
        _LOGGER.info("init")

        # Open settings
        await self._settings_mgr.open()
        if "theme" in self._settings:
            await self.activate_theme(self._settings["theme"], reload=False, save=False)
        for sector in self._sectors:
            sector.init()

        # Open connections
        await self._telemetry.open()
        await self._encoder.open()
        await self._leds.open()
        await self._servos.open()
        await self._sound.open()

    async def close(self):
        _LOGGER.info("close")
        await self._settings_mgr.close()
        await self._telemetry.close()
        await self._leds.close()
        await self._servos.close()
        await self._encoder.close()
        await self._sound.close()
        if self._active_task is not None and not self._active_task.done():
            self._active_task.cancel()

    async def set_state(self, state: WheelStateIn):
        if state.theme is not None:
            await self.activate_theme(state.theme)

        for sector_state in state.sectors:
            if sector_state.index < 0 or sector_state.index >= len(self._sectors):
                raise ValueError("Sector index out of bounds")
            sector = self._sectors[sector_state.index]
            sector.set_state(sector_state)

        if state.servos:
            await self._servos.set_state(state.servos)
        
        if state.leds:
            await self._leds.set_state(state.leds)

        if state.sound:
            await self._sound.set_state(state.sound)

    async def get_state(self) -> WheelState:
        sectors_state = [sector.get_state() for sector in self._sectors]

        themes_state = [
            ThemeState(
                id=theme._id,
                name=theme.name,
                description=theme.description,
                based_on=theme.based_on,
                theme_sound=theme.theme_sound,
            ) for theme in self._themes.values()
        ]

        effects_state = [
            EffectState(
                id=effect._id,
                name=effect.name,
                description=effect.description,
                based_on=effect.based_on,
                effect_sound=effect.effect_sound,
            ) for effect in self._effects.values()
        ]

        servos_state, leds_state, sound_system_state = await asyncio.gather( # type: ignore
            self._servos.get_state(),
            self._leds.get_state(),
            self._sound.get_state(),
        )

        return WheelState(
            theme=self._theme._id,
            sectors=sectors_state,
            themes=themes_state,
            effects=effects_state,
            encoder=self._encoder.get_state(),
            servos=servos_state,
            leds=leds_state,
            sound=sound_system_state,
        )

    def subscribe(self, callback: Callable[[WheelStateUpdate], None]):
        self._subscriptions.append(callback)

    async def activate_theme(self, theme_id: str, reload=True, save=True):
        _LOGGER.info("activate_theme: %s" % (theme_id))
        
        new_theme = self._themes.get(theme_id)
        if new_theme is None:
            raise ValueError("unknown theme name")
        
        if new_theme._id == self._theme._id:
            return
        
        self._theme = new_theme
        if reload:
            self._reload_task()
        if save:
            self._settings.set("theme", self._theme._id)

        self._publish_update(WheelStateUpdate(
            theme=self._theme._id,
        ))

    async def maintain(self):
        _LOGGER.info("maintain...")
        await asyncio.gather(
            self._settings_mgr.maintain(),
            self._encoder.maintain(),
            self._telemetry.maintain(),
            self._leds.maintain(),
            self._servos.maintain(),
            self._sound.maintain(),
            self._maintain(),
            self._maintain_power_state(),
        )
        _LOGGER.info("maintain finished.")

    async def _maintain_power_state(self):
        _LOGGER.info("start maintaining power state")
        while True:
            if self._gpio.input(self._poweroff_pin):
                _LOGGER.info("poweroff requested...")
                self._schedule_task("poweroff")

            await asyncio.sleep(1.0)

    async def _maintain(self):
        _LOGGER.info("start maintaining")
        self._next_task_name = "startup"

        while True:
            # Start next task
            task_name = self._next_task_name
            self._next_task_name = "idle"
            task_co = {
                "startup": self._task_startup,
                "idle": self._task_idle,
                "spinning": self._task_spinning,
                "stopped": self._task_stopped,
                "poweroff": self._task_poweroff,
            }[task_name]()
            _LOGGER.info("start task: %s" % (task_name))
            self._active_task = asyncio.create_task(task_co, name=task_name)

            # Wait for task
            try:
                await self._active_task
            except asyncio.CancelledError:
                _LOGGER.info("task was cancelled: %s" % (self._active_task.get_name()))
                pass
            _LOGGER.info("task finished: %s" % (self._active_task.get_name()))

    def _schedule_task(self, task_name: str):
        cur_task_name = None
        if self._active_task is not None:
            cur_task_name = self._active_task.get_name()

        if task_name == cur_task_name:
            return
        
        if cur_task_name == "poweroff":
            _LOGGER.warn("Cannot schedule tasks after poweroff")
            return

        _LOGGER.info("_schedule_task %s -> %s:" % (cur_task_name, task_name))
        self._next_task_name = task_name
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
        await self._sound.fadeout_all()
        await self._leds.set_state(LedsStateIn(segments=self._theme.idle_led_preset))
        while True:
            _LOGGER.info("idle heartbeat")
            await asyncio.sleep(15.0)

    async def _task_spinning(self):
        enc_state = self._encoder.get_state()
        start_sector = enc_state.sector
        start_sector_count = enc_state.total_sectors
        start_time = self._loop.time()
        try:
            await self._sound.fadeout_all()
            await self._leds.set_state(LedsStateIn(segments=self._theme.spinning_led_preset))
            self._theme_sound_channel = await self._sound.play_sound(self._theme.theme_sound)
            while True:
                await asyncio.sleep(1.0)
        finally:
            end_sector = enc_state.sector
            end_sector_count = enc_state.total_sectors
            end_time = self._loop.time()
            duration = end_time - start_time
            total_sectors = end_sector_count - start_sector_count
            avg_rpm = total_sectors / enc_state.num_sectors / duration * 60.0

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

            if self._theme_sound_channel is not None:
                self._theme_sound_channel.set_volume(0.2)
                await asyncio.sleep(0.2)

            await self._leds.set_state(LedsStateIn(segments=effect.leds_preset))
            await self._sound.play_sound(effect.effect_sound)
            await asyncio.sleep(2.0)

            if self._theme_sound_channel is not None:
                for i in range(2, 11, 1):
                    self._theme_sound_channel.set_volume(i / 10)
                    await asyncio.sleep(0.1)

            await asyncio.sleep(4.0)

            await self._servos.set_state(ServosStateIn.model_validate({"motors": {"bottom": {"pos": 0.0}}}))
            await asyncio.sleep(3.0)
            await self._sound.fadeout_all(timeout_ms=2000)

        finally:
            await self._sound.fadeout_all()
            await self._servos.set_state(ServosStateIn.model_validate({"motors": {"bottom": {"pos": 0.0}}}))

    async def _task_poweroff(self):
        await self._sound.fadeout_all()
        await self._leds.set_state(LedsStateIn(segments=self._theme.poweroff_led_preset))
        while True:
            await asyncio.sleep(5.0)

    async def __aenter__(self):
        await self.init()
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _encoder_event(self, event_name: str):
        _LOGGER.debug("encoder event: %s" % (event_name))
        if event_name == "spinning":
            self._schedule_task("spinning")
        elif event_name == "standstill":
            self._schedule_task("stopped")
        
        self._publish_update(WheelStateUpdate(
            encoder=self._encoder.get_state()
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
        return self._sound
    
    @property
    def sectors(self):
        return self._sectors
    
