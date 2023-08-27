from fastapi import APIRouter, Depends
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import SoundSystemState, SoundSystemStateIn

router = APIRouter(tags=["sound"])


@router.get("/api/v1/sound")
async def get_state(wheel=Depends(get_wheel)) -> SoundSystemState:
    state = await wheel.sound.get_state()
    return state


@router.patch("/api/v1/sound")
async def set_state(state: SoundSystemStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.sound.set_state(state)
    await ws_mgr.broadcast_sound_state()


@router.post("/api/v1/sound/{name}/play")
async def play_sound(name: str, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.sound.play_sound(name)
    await ws_mgr.broadcast_sound_state()
