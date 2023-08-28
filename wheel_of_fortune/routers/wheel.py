from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import WheelState, WheelStateIn

router = APIRouter(tags=["wheel"])


@router.get("/api/v1/wheel")
async def get_state(wheel=Depends(get_wheel)) -> WheelState:
    state = await wheel.get_state()
    return state


@router.patch("/api/v1/wheel")
async def set_state(state: WheelStateIn, wheel=Depends(get_wheel)):
    await wheel.set_state(state)
