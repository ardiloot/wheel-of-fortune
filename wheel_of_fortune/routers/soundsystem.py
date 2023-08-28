from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import SoundSystemState, SoundSystemStateIn

router = APIRouter(tags=["soundsystem"])


@router.get("/api/v1/soundsystem")
async def get_state(wheel=Depends(get_wheel)) -> SoundSystemState:
    state = wheel.sound.get_state()
    return state


@router.patch("/api/v1/soundsystem")
async def set_state(state: SoundSystemStateIn, wheel=Depends(get_wheel)):
    await wheel.sound.set_state(state)
