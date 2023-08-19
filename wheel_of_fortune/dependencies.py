import sys
import asyncio
import logging
from ._config import Config
from ._wheel import Wheel
import OPi.GPIO as GPIO
from fastapi import WebSocket, WebSocketDisconnect
from .schemas import (
    WsCommandPacket,
    WsCommandType,
    WsStateData,
    EncoderState,
    ServosState,
    LedsState,
    SoundSystemState,
    WheelState,
    SoundSystemStateIn,
    LedsStateIn
)

_LOGGER = logging.getLogger(__name__)
wheel = None
maintain_wheel_task = None
ws_manager = None


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
                packet = await self._websocket.receive_json()
                cmd = packet.get("cmd")
                if cmd == "set_sound":
                    data = SoundSystemStateIn.model_validate(packet.get("data", {}))
                    await self._mgr._wheel.sound.set_state(**data.model_dump())
                    await self._mgr.brodcast_sound_state()
                elif cmd == "set_leds":
                    data = LedsStateIn.model_validate(packet.get("data", {}))
                    await self._mgr._wheel.leds.set_state(**data.model_dump())
                    await self._mgr.brodcast_leds_state()
        except WebSocketDisconnect:
            self._mgr._disconnect(self)

    async def send_json(self, data):
        await self._websocket.send_json(data)

    async def _send_state(self):
        wheel = self._mgr._wheel
        servos_state, leds_state, sound_system_state, wheel_state = await asyncio.gather( # type: ignore
            wheel.servos.get_state(),
            wheel.leds.get_state(),
            wheel.sound.get_state(),
            wheel.get_state(),
        )
        
        packet = WsCommandPacket(
            cmd=WsCommandType.state,
            data=WsStateData(
                encoder=EncoderState.model_validate(wheel.encoder.get_state()),
                servos=ServosState.model_validate(servos_state),
                leds=LedsState.model_validate(leds_state),
                sound=SoundSystemState.model_validate(sound_system_state),
                wheel=WheelState.model_validate(wheel_state),
            ),
        )
        await self.send_json(packet.model_dump())


class WsManager:

    def __init__(self, wheel):
        self._wheel: 'Wheel' = wheel
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
    
    async def brodcast_leds_state(self):
        state = await self._wheel.leds.get_state()
        await self._broadcast_json({
            "cmd": "update",
            "data": {
                "leds": state,
            },
        })

    async def brodcast_servos_state(self):
        state = await self._wheel.servos.get_state()
        await self._broadcast_json({
            "cmd": "update",
            "data": {
                "servos": state,
            },
        })

    async def brodcast_sound_state(self):
        state = await self._wheel.sound.get_state()
        await self._broadcast_json({
            "cmd": "update",
            "data": {
                "sound": state,
            },
        })

    async def brodcast_wheel_state(self):
        state = await self._wheel.get_state()
        await self._broadcast_json({
            "cmd": "update",
            "data": {
                "wheel": state,
            },
        })

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

    def _wheel_update_received(self, data):
        _LOGGER.info("WsManager: wheel update received: %s" % (data))
        task = asyncio.create_task(self._broadcast_json({
            "cmd": "update",
            "data": data,
        }))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)


async def get_wheel() -> Wheel:
    if wheel is None:
        raise ValueError()
    return wheel


async def get_ws_manager() -> WsManager:
    if ws_manager is None:
        raise ValueError()
    return ws_manager


async def startup_event():

    async def maintain_wheel():
        if wheel is None:
            raise ValueError("Cannot maintain wheel")

        _LOGGER.info("maintain_wheel...")
        try:
            await wheel.init()
            await wheel.maintain()
        except Exception:
            _LOGGER.exception("Unrecoverable error in maintain_wheel")
            sys.exit("Unrecoverable error in maintain_wheel") 
        finally:
            await wheel.close()
        _LOGGER.info("maintain_wheel finished.")

    global wheel
    global maintain_wheel_task
    global ws_manager
    if wheel is None:
        config = Config()
    
        gpio = GPIO
        gpio.setwarnings(False)
        gpio.setmode(GPIO.SUNXI)
    
        wheel = Wheel(config, gpio)
        ws_manager = WsManager(wheel)
        maintain_wheel_task = asyncio.create_task(maintain_wheel())


async def shutdown_event():
    if maintain_wheel_task is None:
        return
    
    maintain_wheel_task.cancel()
    # Wait for cancel
    try:
        await maintain_wheel_task
    except asyncio.CancelledError:
        _LOGGER.info("maintain_wheel_task successfully cancelled")
        pass
