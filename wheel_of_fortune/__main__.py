import os
import logging
import coloredlogs
import importlib.metadata
from .dependencies import startup_event, shutdown_event
from .routers import encoder
from .routers import servos
from .routers import leds
from .routers import soundsystem
from .routers import wheel
from .routers import ws

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

_LOGGER = logging.getLogger(__name__)
_VERSION = importlib.metadata.version("wheel_of_fortune")

coloredlogs.install(
    level="debug",
    fmt="%(asctime)s %(name)s:%(lineno)d %(levelname)s %(message)s",
    milliseconds=True,
)

app = FastAPI(docs_url="/api/v1/docs", openapi_url="/api/v1/openapi.json")

app.include_router(encoder.router)
app.include_router(servos.router)
app.include_router(leds.router)
app.include_router(soundsystem.router)
app.include_router(wheel.router)
app.include_router(ws.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

local_www_path = os.environ.get("LOCAL_WWW_PATH")
if local_www_path is not None:
    if os.path.isdir(local_www_path):
        _LOGGER.info("local www path: %s" % (local_www_path))
        app.mount(
            "/local", StaticFiles(directory=local_www_path, html=True), name="local"
        )
    else:
        _LOGGER.warning("local www path does not exist: %s" % (local_www_path))

frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    _LOGGER.warning("frontend path does not exist: %s" % (frontend_path))


@app.on_event("startup")
async def api_startup_event():
    _LOGGER.info("version: %s" % (_VERSION))
    _LOGGER.info("startup_event")
    await startup_event()


@app.on_event("shutdown")
async def api_shutdown_event():
    _LOGGER.info("shutdown_event")
    await shutdown_event()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
