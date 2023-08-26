from enum import Enum
from pydantic import BaseModel, Field


class Versions(BaseModel):
    wled: str


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


class ServoName(str, Enum):
    bottom = "bottom"
    right = "right"
    left = "left"


class ServoStateIn(BaseModel):
    pos: float | None = Field(ge=-0.3, le=1.3, examples=[0.5])
    detached: bool = False


class ServosStateIn(BaseModel):
    servos: dict[str, ServoStateIn] = {}


class ServoState(BaseModel):
    pos: float | None = None
    duty: float
    detached: bool


class ServosState(BaseModel):
    servos: dict[str, ServoState]
    

class LedSegmentState(BaseModel):
    enabled: bool
    brightness: float
    pallete: str
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
    pallete: str | None = "default"
    primary_color: str | None = "#FF0000"
    secondary_color: str | None = "#000000"
    effect: str | None = "solid"
    effect_speed: float | None = Field(default=0.5, ge=0.0, le=1.0)
    effect_intensity: float | None = Field(default=0.5, ge=0.0, le=1.0)


class LedsStateIn(BaseModel):
    brightness: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])
    segments: dict[str, LedSegmentStateIn] | None = None


class SoundState(BaseModel):
    volume: float
    num_playing: int
    duration_secs: float


class SoundSystemState(BaseModel):
    inited: bool
    volume: float
    num_channels: int
    is_busy: bool
    sounds: dict[str, SoundState]


class SoundSystemStateIn(BaseModel):
    volume: float | None = Field(default=None, ge=0.0, le=1.0, examples=[0.5])


class SectorState(BaseModel):
    index: int
    name: str
    effect: str


class ThemeState(BaseModel):
    id: str
    name: str
    description: str
    based_on: list[str]
    theme_sound: str


class EffectState(BaseModel):
    id: str
    name: str
    description: str
    based_on: list[str]
    effect_sound: str


class WheelState(BaseModel):
    theme: str
    sectors: list[SectorState]
    themes: list[ThemeState]
    effects: list[EffectState]


class WheelStateIn(BaseModel):
    theme: str | None = None


class SectorStateIn(BaseModel):
    name: str | None = None
    effect: str | None = None


class WsCommandType(str, Enum):
    state = "state"
    update = "update"


class WsStateData(BaseModel):
    encoder: EncoderState
    servos: ServosState
    leds: LedsState
    sound: SoundSystemState
    wheel: WheelState


class WsCommandPacket(BaseModel):
    cmd: WsCommandType
    data: WsStateData
