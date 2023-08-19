from fastapi import APIRouter, Depends
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import ServoName, ServosState, ServoStateIn

router = APIRouter(tags=["servos"])


@router.get("/api/v1/servos")
async def get_state(wheel=Depends(get_wheel)) -> ServosState:
    res = await wheel.servos.get_state()
    return res


@router.post("/api/v1/servos")
async def set_state(state: ServoStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.servos.set_state(**state.model_dump())
    await ws_mgr.brodcast_servos_state()


@router.post("/api/v1/servos/{name}")
async def set_servo_state(name: ServoName, state: ServoStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.servos.set_state(**state, names=[name])
    await ws_mgr.brodcast_servos_state()
