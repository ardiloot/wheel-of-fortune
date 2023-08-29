from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import ServosState, ServosStateIn

router = APIRouter(tags=["servos"])


@router.get("/api/v1/servos/state")
async def get_state(wheel=Depends(get_wheel)) -> ServosState:
    return wheel.servos.get_state()


@router.patch("/api/v1/servos/state")
async def set_state(state: ServosStateIn, wheel=Depends(get_wheel)):
    await wheel.servos.set_state(state)
