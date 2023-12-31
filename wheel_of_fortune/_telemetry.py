import socket
import asyncio
import logging
import influxdb_client
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from ._config import Config

_LOGGER = logging.getLogger(__name__)


class Point(influxdb_client.Point):
    pass


class Telemetry:
    def __init__(self, config):
        self._config: Config = config
        self._hostname = socket.gethostname()
        self._influxdb = None
        if config.influxdb_url is not None and config.influxdb_token is not None:
            self._influxdb = InfluxDBClientAsync(
                url=config.influxdb_url,
                token=config.influxdb_token,
            )
        self._background_tasks = set()

    async def open(self):
        if self._influxdb is None:
            return
        _LOGGER.info(
            "open, name: %s, hostname: %s" % (self._config.name, self._hostname)
        )

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
        if len(self._background_tasks) > 1000:
            _LOGGER.error(
                "Queue full (%d), discard data point" % (len(self._background_tasks))
            )

        point.tag("name", self._config.name)
        point.tag("host", self._hostname)

        write_api = self._influxdb.write_api()
        task = asyncio.create_task(
            write_api.write(
                self._config.influxdb_bucket, self._config.influxdb_org, point
            )
        )
        self._background_tasks.add(task)
        task.add_done_callback(self._task_finished)

    def _task_finished(self, task):
        try:
            task.result()
        except Exception:
            _LOGGER.error(
                "Error, discard datapoint (%d in queue)" % (len(self._background_tasks))
            )
        finally:
            self._background_tasks.discard(task)
