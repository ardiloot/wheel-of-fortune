import os
import logging
import coloredlogs
import importlib.metadata
from .dependencies import startup_event, shutdown_event
from .routers import encoder
from .routers import servos
from .routers import leds
from .routers import sound
from .routers import wheel
from .routers import ws

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

_LOGGER = logging.getLogger(__name__)
_VERSION = importlib.metadata.version("wheel_of_fortune")

app = FastAPI(
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

app.include_router(encoder.router)
app.include_router(servos.router)
app.include_router(leds.router)
app.include_router(sound.router)
app.include_router(wheel.router)
app.include_router(ws.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


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
    
    coloredlogs.install(
        level="debug",
        fmt="%(asctime)s %(name)s:%(lineno)d %(levelname)s %(message)s",
        milliseconds=True
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)
