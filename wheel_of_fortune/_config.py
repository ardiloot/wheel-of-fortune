from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = [
    "Config",
]


class WLedSegmentConfig(BaseSettings):
    name: str
    start: int
    stop: int


class Config(BaseSettings):
    name: str = "wheel-of-fortune"
    data_dir: str = "./data"
    num_sectors: int = 16

    wled_url: str | None = None
    wled_segments: list[WLedSegmentConfig] = []
    
    influxdb_url: str | None = None
    influxdb_token: str | None = None
    influxdb_org: str | None = None
    influxdb_bucket: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="wheel_",
        env_nested_delimiter="__",
        env_file=".env",
    )
