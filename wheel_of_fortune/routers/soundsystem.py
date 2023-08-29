from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import SoundSystemState, SoundSystemInfo, SoundSystemStateIn

router = APIRouter(tags=["soundsystem"])


@router.get("/api/v1/soundsystem/state")
async def get_state(wheel=Depends(get_wheel)) -> SoundSystemState:
    return wheel.sound.get_state()


@router.get("/api/v1/soundsystem/info")
async def get_info(wheel=Depends(get_wheel)) -> SoundSystemInfo:
    return wheel.sound.get_info()


@router.patch("/api/v1/soundsystem/state")
async def set_state(state: SoundSystemStateIn, wheel=Depends(get_wheel)):
    await wheel.sound.set_state(state)
