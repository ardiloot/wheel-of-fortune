import os
import socket
import asyncio
import logging
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point

_LOGGER = logging.getLogger(__name__)

INFLUXDB_URL = os.environ["INFLUXDB_URL"]
INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]
INFLUXDB_ORG = os.environ["INFLUXDB_ORG"]
INFLUXDB_BUCKET = os.environ["INFLUXDB_BUCKET"]


class Telemetry:

    def __init__(self, name):
        self._name = name
        self._hostname = socket.gethostname()
        self._influxdb = InfluxDBClientAsync(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
        self._background_tasks = set()

    async def open(self):
        _LOGGER.info("open, name: %s, hostname: %s" % (self._name, self._hostname))
        # influxdb_ready = await self._influxdb.ping()
        # _LOGGER.info("InfluxDB ready: %s" % (influxdb_ready))

    async def close(self):
        _LOGGER.info("close")
        await self._influxdb.close()

    async def maintain(self):
        pass

    def report_point(self, point):
        point.tag("name", self._name)
        point.tag("host", self._hostname)

        write_api = self._influxdb.write_api()
        task = asyncio.create_task(write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point))
        self._background_tasks.add(task)
        task.add_done_callback(self._task_finished)

    def _task_finished(self, task):
        try:
            task.result()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout (%d in queue)" % (len(self._background_tasks)))
        finally:
            self._background_tasks.discard(task)