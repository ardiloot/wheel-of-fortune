import sys
import asyncio
import logging
import OPi.GPIO as GPIO
from ._config import Config
from ._wheel import Wheel
from ._ws_manager import WsManager


_LOGGER = logging.getLogger(__name__)

wheel: Wheel | None = None
ws_manager: WsManager | None = None
maintain_wheel_task = None


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
