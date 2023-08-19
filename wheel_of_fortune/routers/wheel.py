from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_wheel, get_ws_manager
from ..schemas import WheelState, WheelStateIn, SectorStateIn

router = APIRouter(tags=["wheel"])


@router.get("/api/v1/wheel")
async def get_state(wheel=Depends(get_wheel)) -> WheelState:
    state = await wheel.get_state()
    return state


@router.post("/api/v1/wheel")
async def set_state(state: WheelStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    await wheel.set_state(**state.model_dump())
    await ws_mgr.brodcast_wheel_state()


@router.post("/api/v1/wheel/sector/{index}")
async def set_sector_state(index: int, state: SectorStateIn, wheel=Depends(get_wheel), ws_mgr=Depends(get_ws_manager)):
    if index < 0 or index >= len(wheel.sectors):
        raise HTTPException(status_code=404, detail="Sector index not found")
    
    sector = wheel.sectors[index]
    await sector.set_state(**state.model_dump())
    await ws_mgr.brodcast_wheel_state()
