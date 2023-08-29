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
    num_sectors: int
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


class ServosState(BaseModel):
    motors: dict[str, ServoState]


class ServoStateIn(BaseModel):
    pos: float | None = Field(ge=-0.3, le=1.3, examples=[0.5])
    detached: bool = False


class ServosStateIn(BaseModel):
    motors: dict[str, ServoStateIn] = {}


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


class LedsState(BaseModel):
    power_on: bool
    brightness: float
    segments: dict[str, LedSegmentState]


class LedSegmentStateIn(BaseModel):
    enabled: bool | None = True
    brightness: float | None = Field(default=1.0, ge=0.0, le=1.0)
    palette: str | None = "default"
    primary_color: str | None = "#FF0000"
    secondary_color: str | None = "#000000"
    effect: str | None = "solid"
    effect_speed: float | None = Field(default=0.5, ge=0.0, le=1.0)
    effect_intensity: float | None = Field(default=0.5, ge=0.0, le=1.0)


class LedsStateIn(BaseModel):
    brightness: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])
    segments: dict[str, LedSegmentStateIn] | None = None


# -----------------------------------------------------------------------------
# Sound system
# -----------------------------------------------------------------------------


class SoundState(BaseModel):
    volume: float
    duration_secs: float


class SoundChannelState(BaseModel):
    volume: float
    sound_name: str | None


class SoundSystemState(BaseModel):
    channels: dict[str, SoundChannelState]
    sounds: dict[str, SoundState]


class SoundChannelStateIn(BaseModel):
    volume: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])
    sound_name: str | None = None


class SoundSystemStateIn(BaseModel):
    channels: dict[str, SoundChannelStateIn] = {}


# -----------------------------------------------------------------------------
# Sectors
# -----------------------------------------------------------------------------


class SectorState(BaseModel):
    index: int
    name: str
    effect: str


class SectorStateIn(BaseModel):
    name: str | None = None
    effect: str | None = None


# -----------------------------------------------------------------------------
# Themes
# -----------------------------------------------------------------------------


class ThemeState(BaseModel):
    id: str
    name: str
    description: str
    based_on: list[str]
    theme_sound: str


# -----------------------------------------------------------------------------
# Effects
# -----------------------------------------------------------------------------


class EffectState(BaseModel):
    id: str
    name: str
    description: str
    based_on: list[str]
    effect_sound: str


# -----------------------------------------------------------------------------
# Wheel
# -----------------------------------------------------------------------------


class WheelState(BaseModel):
    task_name: str | None
    theme: str
    themes: list[ThemeState]
    sectors: list[SectorState]
    effects: list[EffectState]
    encoder: EncoderState
    servos: ServosState
    leds: LedsState
    soundsystem: SoundSystemState


class WheelStateIn(BaseModel):
    theme: str | None = None
    sectors: dict[int, SectorStateIn] = {}
    servos: ServosStateIn | None = None
    leds: LedsStateIn | None = None
    soundsystem: SoundSystemStateIn | None = None


class WheelStateUpdate(BaseModel):
    task_name: str | None = None
    theme: str | None = None
    sectors: list[SectorState] | None = None
    encoder: EncoderState | None = None
    servos: ServosState | None = None
    leds: LedsState | None = None
    soundsystem: SoundSystemState | None = None


# -----------------------------------------------------------------------------
# Websocket
# -----------------------------------------------------------------------------


class WsCommandType(Enum):
    STATE = "state"    # Full state (to client)
    UPDATE = "update"       # State update (to client)
    SET_STATE = "set_state" # Set state (to server)


class WsStatePacket(BaseModel):
    cmd: WsCommandType = WsCommandType.STATE
    ts: float
    state: WheelState


class WsUpdatePacket(BaseModel):
    cmd: WsCommandType = WsCommandType.UPDATE
    ts: float
    update: WheelStateUpdate


class WsSetStatePacket(BaseModel):
    cmd: WsCommandType = WsCommandType.SET_STATE
    ts: float
    state: WheelStateIn
