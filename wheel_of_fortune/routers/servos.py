from fastapi import APIRouter, Depends
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import ServoName, ServosState, ServoStateIn, ServosStateIn

router = APIRouter(tags=["servos"])


@router.get("/api/v1/servos")
async def get_state(wheel=Depends(get_wheel)) -> ServosState:
    res = await wheel.servos.get_state()
    return res


@router.patch("/api/v1/servos")
async def set_state(state: ServosStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.servos.set_state(state)
