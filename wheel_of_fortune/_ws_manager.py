import time
import asyncio
import logging
from typing import TYPE_CHECKING
from fastapi import WebSocket, WebSocketDisconnect
from .schemas import (
    WsCommandType,
    WsInitPacket,
    WheelStateUpdate,
    WsUpdatePacket,
    WsSetStatePacket,
)

if TYPE_CHECKING:
    from ._wheel import Wheel


_LOGGER = logging.getLogger(__name__)


class WsConnection:
    def __init__(self, mgr, websocket):
        self._mgr: "WsManager" = mgr
        self._websocket: WebSocket = websocket

    async def connect(self):
        _LOGGER.info("Accept WS connection %s" % (str(self._websocket.client)))
        await self._websocket.accept()
        await self._send_init()

    async def maintain(self):
        try:
            while True:
                packet_json = await self._websocket.receive_json()
                cmd = WsCommandType(packet_json.get("cmd"))
                if cmd == WsCommandType.SET_STATE:
                    packet = WsSetStatePacket.model_validate(packet_json)
                    await self._mgr._wheel.set_state(packet.state)
                else:
                    raise ValueError("Unknown packet: %s" % (packet_json))
        except WebSocketDisconnect:
            self._mgr._disconnect(self)

    async def send(self, data: str):
        try:
            await self._websocket.send_text(data)
        except Exception:
            _LOGGER.exception(
                "Unable to send WS data: %s" % (str(self._websocket.client))
            )
            self._mgr._disconnect(self)

    async def _send_init(self):
        wheel = self._mgr._wheel
        packet = WsInitPacket(
            ts=time.time(),
            state=wheel.get_state(),
            info=wheel.get_info(),
        )
        await self.send(packet.model_dump_json())


class WsManager:
    def __init__(self, wheel):
        self._wheel: Wheel = wheel
        self._connections: set[WsConnection] = set()
        self._wheel.subscribe(self._wheel_update_received)
        self._background_tasks = set()

    async def add_client(self, websocket: WebSocket) -> WsConnection | None:
        _LOGGER.info(
            "WsManager: add client %s (num_connections: %d)"
            % (websocket.client, len(self._connections) + 1)
        )

        try:
            connection = WsConnection(self, websocket)
            await connection.connect()
            self._connections.add(connection)
        except Exception:
            _LOGGER.exception(
                "Failed to connect to WS client: %s" % (str(websocket.client))
            )
            connection = None
        return connection

    async def _broadcast_update(self, update: WheelStateUpdate):
        packet = WsUpdatePacket(
            ts=time.time(),
            update=update,
        )
        await self._broadcast(packet.model_dump_json(exclude_none=True))

    async def _broadcast(self, data: str):
        r = []
        for connection in self._connections:
            r.append(connection.send(data))
        await asyncio.gather(*r)

    def _disconnect(self, connection: WsConnection):
        if connection not in self._connections:
            return
        _LOGGER.info(
            "WsManager: disconnected %s (num_connections: %d)"
            % (str(connection._websocket.client), len(self._connections) - 1)
        )
        self._connections.remove(connection)

    def _wheel_update_received(self, update: WheelStateUpdate):
        task = asyncio.create_task(self._broadcast_update(update))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
