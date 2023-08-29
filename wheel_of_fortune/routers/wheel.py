from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import WheelState, WheelInfo, WheelStateIn

router = APIRouter(tags=["wheel"])


@router.get("/api/v1/wheel/state")
async def get_state(wheel=Depends(get_wheel)) -> WheelState:
    return wheel.get_state()


@router.get("/api/v1/wheel/info")
async def get_info(wheel=Depends(get_wheel)) -> WheelInfo:
    return wheel.get_info()


@router.patch("/api/v1/wheel/state")
async def set_state(state: WheelStateIn, wheel=Depends(get_wheel)):
    await wheel.set_state(state)
