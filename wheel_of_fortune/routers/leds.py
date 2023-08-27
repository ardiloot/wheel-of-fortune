from fastapi import APIRouter, Depends
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import LedsState, LedsStateIn

router = APIRouter(tags=["leds"])


@router.get("/api/v1/leds")
async def get_state(wheel=Depends(get_wheel)) -> LedsState:
    state = await wheel.leds.get_state()
    return state


@router.patch("/api/v1/leds")
async def set_state(state: LedsStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.leds.set_state(state)
    await ws_mgr.broadcast_leds_state()
    
