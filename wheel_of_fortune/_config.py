import math
from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = [
    "Config",
]


class ServoConfig(BaseSettings):
    name: str
    mount_angle: float


class WLedSegmentConfig(BaseSettings):
    name: str
    start: int
    stop: int


class Config(BaseSettings):
    name: str = "wheel-of-fortune"
    display_name: str = "Wheel of Fortune"
    logo_url: str = "logo_url"
    data_dir: str = "./data"
    num_sectors: int = 16

    wled_url: str | None = None
    wled_segments: list[WLedSegmentConfig] = []

    servos: list[ServoConfig] = [
        ServoConfig(name="bottom", mount_angle=math.radians(0.0)),
        ServoConfig(name="right", mount_angle=math.radians(-135)),
        ServoConfig(name="left", mount_angle=math.radians(135)),
    ]
    servo_zero_duty: float = 0.0912
    servo_full_duty: float = 0.0516
    servo_mount_duty: float = 0.0473

    influxdb_url: str | None = None
    influxdb_token: str | None = None
    influxdb_org: str | None = None
    influxdb_bucket: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="wheel_",
        env_nested_delimiter="__",
        env_file=".env",
    )
