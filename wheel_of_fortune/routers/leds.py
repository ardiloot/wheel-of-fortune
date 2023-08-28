from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import LedsState, LedsStateIn

router = APIRouter(tags=["leds"])


@router.get("/api/v1/leds")
async def get_state(wheel=Depends(get_wheel)) -> LedsState:
    state = wheel.leds.get_state()
    return state


@router.patch("/api/v1/leds")
async def set_state(state: LedsStateIn, wheel=Depends(get_wheel)):
    await wheel.leds.set_state(state)
    
