from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from .core.config import settings
from .database import get_db, engine, Base
from .api.v1 import api_router
from .websockets.manager import manager
import os

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    return FileResponse("templates/index.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page"""
    return FileResponse("templates/login.html")


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Serve the register page"""
    return FileResponse("templates/register.html")


@app.get("/board/{board_id}", response_class=HTMLResponse)
async def board_page(board_id: str):
    """Serve the board page"""
    return FileResponse("templates/board.html")


@app.websocket("/ws/board/{board_id}")
async def websocket_board(websocket: WebSocket, board_id: str):
    """WebSocket endpoint for real-time board updates"""
    await manager.connect(websocket, board_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast the update to all connected clients on this board
            await manager.broadcast_to_board(board_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, board_id)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
