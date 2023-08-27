from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import WheelState, WheelStateIn, SectorStateIn

router = APIRouter(tags=["wheel"])


@router.get("/api/v1/wheel")
async def get_state(wheel=Depends(get_wheel)) -> WheelState:
    state = await wheel.get_state()
    return state


@router.patch("/api/v1/wheel")
async def set_state(state: WheelStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.set_state(state)
    await ws_mgr.broadcast_wheel_state()
