from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = [
    "Config",
]


class WLedSegmentConfig(BaseSettings):
    name: str
    start: int
    stop: int


class InfluxdbConfig(BaseSettings):
    url: str | None = None
    token: str | None = None
    org: str | None = None
    bucket: str | None = None


class Config(BaseSettings):
    name: str = "wheel-of-fortune"
    wled_url: str | None = None
    wled_segments: list[WLedSegmentConfig] = []
    influxdb: InfluxdbConfig | None = None

    model_config = SettingsConfigDict(
        env_prefix="wheel_",
        env_nested_delimiter="__",
        env_file=".env",
    )
