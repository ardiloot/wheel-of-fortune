from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import LedsState, LedsInfo, LedsStateIn

router = APIRouter(tags=["leds"])


@router.get("/api/v1/leds/state")
async def get_state(wheel=Depends(get_wheel)) -> LedsState:
    return wheel.leds.get_state()


@router.get("/api/v1/leds/info")
async def get_info(wheel=Depends(get_wheel)) -> LedsInfo:
    return wheel.leds.get_info()


@router.patch("/api/v1/leds/state")
async def set_state(state: LedsStateIn, wheel=Depends(get_wheel)):
    await wheel.leds.set_state(state)
