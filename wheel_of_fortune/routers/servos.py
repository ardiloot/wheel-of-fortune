from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import ServosState, ServosStateIn

router = APIRouter(tags=["servos"])


@router.get("/api/v1/servos")
async def get_state(wheel=Depends(get_wheel)) -> ServosState:
    res = wheel.servos.get_state()
    return res


@router.patch("/api/v1/servos")
async def set_state(state: ServosStateIn, wheel=Depends(get_wheel)):
    await wheel.servos.set_state(state)
