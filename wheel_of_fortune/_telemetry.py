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
        self._influxdb = InfluxDBClientAsync(
            url=config.influxdb.url,
            token=config.influxdb.token,
        )
        self._background_tasks = set()

    async def open(self):
        _LOGGER.info("open, name: %s, hostname: %s" % (self._config.name, self._hostname))
        # influxdb_ready = await self._influxdb.ping()
        # _LOGGER.info("InfluxDB ready: %s" % (influxdb_ready))

    async def close(self):
        _LOGGER.info("close")
        await self._influxdb.close()

    async def maintain(self):
        pass

    def report_point(self, point):
        point.tag("name", self._config.name)
        point.tag("host", self._hostname)

        write_api = self._influxdb.write_api()
        task = asyncio.create_task(
            write_api.write(self._config.influxdb.bucket, self._config.influxdb.org, point)
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