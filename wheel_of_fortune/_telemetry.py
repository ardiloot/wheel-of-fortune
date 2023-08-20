import socket
import asyncio
import logging
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point
from ._config import Config

_LOGGER = logging.getLogger(__name__)


class Telemetry:

    def __init__(self, config):
        self._config: Config = config
        self._hostname = socket.gethostname()
        self._influxdb = None
        if (
            config.influxdb_url is not None and
            config.influxdb_token is not None
        ):
            self._influxdb = InfluxDBClientAsync(
                url=config.influxdb_url,
                token=config.influxdb_token,
            )
        self._background_tasks = set()

    async def open(self):
        if self._influxdb is None:
            return
        _LOGGER.info("open, name: %s, hostname: %s" % (self._config.name, self._hostname))
        influxdb_ready = await self._influxdb.ping()
        _LOGGER.info("InfluxDB ready: %s" % (influxdb_ready))

    async def close(self):
        if self._influxdb is None:
            return
        _LOGGER.info("close")
        await self._influxdb.close()

    async def maintain(self):
        pass

    def report_point(self, point):
        if self._influxdb is None:
            return
        if self._config.influxdb_bucket is None or self._config.influxdb_org is None:
            return
        
        point.tag("name", self._config.name)
        point.tag("host", self._hostname)

        write_api = self._influxdb.write_api()
        task = asyncio.create_task(
            write_api.write(self._config.influxdb_bucket, self._config.influxdb_org, point)
        )
        self._background_tasks.add(task)
        task.add_done_callback(self._task_finished)

    def _task_finished(self, task):
        try:
            task.result()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout (%d in queue)" % (len(self._background_tasks)))
        finally:
            self._background_tasks.discard(task)
