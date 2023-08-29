from fastapi import APIRouter, Depends
from ..dependencies import get_wheel
from ..schemas import EncoderState, EncoderTestParams

router = APIRouter(tags=["encoder"])


@router.get("/api/v1/encoder/state")
def get_state(wheel=Depends(get_wheel)) -> EncoderState:
    return wheel.encoder.get_state()


@router.post("/api/v1/encoder/test")
async def test_encoder(params: EncoderTestParams, wheel=Depends(get_wheel)):
    await wheel.encoder.test(
        initial_speed=params.initial_speed,
        drag_factor=params.drag_factor,
    )
