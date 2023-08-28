import time
import asyncio
import logging
from typing import TYPE_CHECKING
from fastapi import WebSocket, WebSocketDisconnect
from .schemas import (
    WsCommandType,
    WsStatePacket,
    WheelStateUpdate,
    WsUpdatePacket,
    WsSetStatePacket,
)

if TYPE_CHECKING:
    from ._wheel import Wheel


_LOGGER = logging.getLogger(__name__)


class WsConnection:

    def __init__(self, mgr, websocket):
        self._mgr: 'WsManager' = mgr
        self._websocket: WebSocket = websocket

    async def connect(self):
        _LOGGER.info("Accept WS connection %s" % (self._websocket))
        await self._websocket.accept()
        await self._send_state()

    async def maintain(self):
        try:
            while True:
                packet_json = await self._websocket.receive_json()
                cmd = packet_json.get("cmd")
                if cmd == WsCommandType.set_state:
                    packet = WsSetStatePacket.model_validate(packet_json)
                    await self._mgr._wheel.set_state(packet.state)
                else:
                    raise ValueError("Unknown packet: %s" % (packet_json))
        except WebSocketDisconnect:
            self._mgr._disconnect(self)

    async def send_json(self, data):
        await self._websocket.send_json(data)

    async def _send_state(self):
        wheel = self._mgr._wheel
        state = await wheel.get_state()
        packet = WsStatePacket(
            ts=time.time(),
            state=state,
        )
        await self.send_json(packet.model_dump())


class WsManager:

    def __init__(self, wheel):
        self._wheel: Wheel = wheel
        self._connections: set[WsConnection] = set()
        self._wheel.subscribe(self._wheel_update_received)
        self._background_tasks = set()

    async def connect(self, websocket: WebSocket) -> WsConnection:
        _LOGGER.info("WsManager: add connection %s (num_connections: %d)" % (
            websocket,
            len(self._connections) + 1
        ))
        connection = WsConnection(self, websocket)
        self._connections.add(connection)
        await connection.connect()
        return connection
    
    async def _broadcast_update(self, update: WheelStateUpdate):
        packet = WsUpdatePacket(
            ts=time.time(),
            update=update,
        )
        await self._broadcast_json(packet.model_dump(exclude_none=True))

    async def _broadcast_json(self, data):
        _LOGGER.info("WsManager: broadcast json to %d clients" % (len(self._connections)))
        r = []
        for connection in self._connections:
            r.append(connection.send_json(data))
        await asyncio.gather(*r)

    def _disconnect(self, connection: WsConnection):
        _LOGGER.info("WsManager: disconnected %s (num_connections: %d)" % (
            connection._websocket,
            len(self._connections) - 1
        ))
        self._connections.remove(connection)

    def _wheel_update_received(self, update: WheelStateUpdate):
        _LOGGER.info("WsManager: wheel state update received: %s" % (update))
        task = asyncio.create_task(self._broadcast_update(update))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
