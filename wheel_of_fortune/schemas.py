from enum import Enum
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Encoder
# -----------------------------------------------------------------------------


class EncoderState(BaseModel):
    sector: int
    rpm: float
    total_revs: float
    total_sectors: int
    missed_sector_count: int
    standstill: bool


class EncoderTestParams(BaseModel):
    initial_speed: float = Field(ge=0.0, le=100, examples=[20])
    drag_factor: float = Field(ge=0.0, le=100, examples=[0.1])


# -----------------------------------------------------------------------------
# Servos
# -----------------------------------------------------------------------------


class ServoState(BaseModel):
    pos: float
    duty: float
    detached: bool


class ServoStateIn(BaseModel):
    pos: float | None = Field(default=None, ge=-0.3, le=1.3, examples=[0.5])
    detached: bool | None = None


class ServoInfo(BaseModel):
    mount_angle: float
    zero_duty: float
    full_duty: float
    mount_duty: float
    mount_pos: float


class ServosState(BaseModel):
    motors: dict[str, ServoState]


class ServosStateIn(BaseModel):
    motors: dict[str, ServoStateIn] = {}


class ServosInfo(BaseModel):
    version: str
    motors: dict[str, ServoInfo]


# -----------------------------------------------------------------------------
# LEDs
# -----------------------------------------------------------------------------


class LedSegmentState(BaseModel):
    enabled: bool
    brightness: float
    palette: str
    primary_color: str
    secondary_color: str
    effect: str
    effect_speed: float
    effect_intensity: float


class LedSegmentStateIn(BaseModel):
    enabled: bool | None = True
    brightness: float | None = Field(default=1.0, ge=0.0, le=1.0)
    palette: str | None = "default"
    primary_color: str | None = "#FF0000"
    secondary_color: str | None = "#000000"
    effect: str | None = "solid"
    effect_speed: float | None = Field(default=0.5, ge=0.0, le=1.0)
    effect_intensity: float | None = Field(default=0.5, ge=0.0, le=1.0)


class LedsState(BaseModel):
    power_on: bool
    brightness: float
    segments: dict[str, LedSegmentState]


class LedsStateIn(BaseModel):
    brightness: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])
    segments: dict[str, LedSegmentStateIn] | None = None
    transition_ms: float = 0.0


class LedsInfo(BaseModel):
    version: str


# -----------------------------------------------------------------------------
# Sound system
# -----------------------------------------------------------------------------


class SoundChannelState(BaseModel):
    volume: float
    sound_name: str | None


class SoundChannelStateIn(BaseModel):
    volume: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])
    sound_name: str | None = None


class SoundSystemState(BaseModel):
    channels: dict[str, SoundChannelState]


class SoundSystemStateIn(BaseModel):
    channels: dict[str, SoundChannelStateIn] = {}


class SoundInfo(BaseModel):
    duration_secs: float


class SoundSystemInfo(BaseModel):
    sounds: dict[str, SoundInfo]


# -----------------------------------------------------------------------------
# Sectors
# -----------------------------------------------------------------------------


class SectorState(BaseModel):
    index: int
    name: str
    effect_id: str


class SectorStateIn(BaseModel):
    name: str | None = None
    effect_id: str | None = None


# -----------------------------------------------------------------------------
# Themes
# -----------------------------------------------------------------------------


class ThemeInfo(BaseModel):
    name: str
    description: str
    image_url: str
    based_on: list[str] = []
    startup_sound: str
    theme_sounds: list[str]
    poweroff_sound: str
    startup_led_preset: dict[str, LedSegmentStateIn]
    idle_led_preset: dict[str, LedSegmentStateIn]
    spinning_led_preset: dict[str, LedSegmentStateIn]
    standby_led_preset: dict[str, LedSegmentStateIn]
    poweroff_led_preset: dict[str, LedSegmentStateIn]


# -----------------------------------------------------------------------------
# Effects
# -----------------------------------------------------------------------------


class EffectInfo(BaseModel):
    name: str
    description: str
    image_url: str
    color: str
    based_on: list[str] = []
    effect_sound: str
    leds_preset: dict[str, LedSegmentStateIn]
    active_servos: list[str]


# -----------------------------------------------------------------------------
# Wheel
# -----------------------------------------------------------------------------


class WheelState(BaseModel):
    active_task: str
    theme_id: str
    standby_timer: float
    sectors: list[SectorState]
    encoder: EncoderState
    servos: ServosState
    leds: LedsState
    soundsystem: SoundSystemState


class WheelStateIn(BaseModel):
    active_task: str | None = None
    theme_id: str | None = None
    standby_timer: float | None = Field(default=None, examples=[600])
    sectors: dict[int, SectorStateIn] = {}
    servos: ServosStateIn | None = None
    leds: LedsStateIn | None = None
    soundsystem: SoundSystemStateIn | None = None


class WheelStateUpdate(BaseModel):
    active_task: str | None = None
    theme_id: str | None = None
    standby_timer: float | None = None
    sectors: list[SectorState] | None = None
    encoder: EncoderState | None = None
    servos: ServosState | None = None
    leds: LedsState | None = None
    soundsystem: SoundSystemState | None = None


class WheelInfo(BaseModel):
    version: str
    name: str
    display_name: str
    logo_name: str
    themes: dict[str, ThemeInfo]
    effects: dict[str, EffectInfo]
    servos: ServosInfo
    leds: LedsInfo
    soundsystem: SoundSystemInfo


# -----------------------------------------------------------------------------
# Websocket
# -----------------------------------------------------------------------------


class WsCommandType(Enum):
    INIT = "init"  # Full state and info (to client)
    UPDATE = "update"  # State update (to client)
    SET_STATE = "set_state"  # Set state (to server)


class WsInitPacket(BaseModel):
    cmd: WsCommandType = WsCommandType.INIT
    ts: float
    state: WheelState
    info: WheelInfo


class WsUpdatePacket(BaseModel):
    cmd: WsCommandType = WsCommandType.UPDATE
    ts: float
    update: WheelStateUpdate


class WsSetStatePacket(BaseModel):
    cmd: WsCommandType = WsCommandType.SET_STATE
    ts: float
    state: WheelStateIn
