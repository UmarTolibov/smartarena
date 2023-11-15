from fastapi import WebSocket
from fastapi.responses import HTMLResponse

from config import html


async def get():
    return HTMLResponse(html)


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for data in websocket.iter_text():
        try:
            await websocket.send_text(f"square of {data} is: {int(data) ** 2}")
        except ValueError:
            await websocket.send_text(f"Message text was: {data}, which is not a squarable input")

