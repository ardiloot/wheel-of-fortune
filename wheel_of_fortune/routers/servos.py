from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import ServosState, ServosInfo, ServosStateIn

router = APIRouter(tags=["servos"])


@router.get("/api/v1/servos/state")
async def get_state(wheel=Depends(get_wheel)) -> ServosState:
    return wheel.servos.get_state()


@router.get("/api/v1/servos/info")
async def get_info(wheel=Depends(get_wheel)) -> ServosInfo:
    return wheel.servos.get_info()


@router.patch("/api/v1/servos/state")
async def set_state(state: ServosStateIn, wheel=Depends(get_wheel)):
    await wheel.servos.set_state(state)
