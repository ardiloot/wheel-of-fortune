from fastapi import APIRouter, Depends, WebSocket
from ..dependencies import get_ws_manager


router = APIRouter(tags=["ws"])


@router.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket, ws_manager=Depends(get_ws_manager)):
    connection = await ws_manager.connect(websocket)
    await connection.maintain()
