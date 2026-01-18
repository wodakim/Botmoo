from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import logging
from simulation import WorldEngine
import json
from contextlib import asynccontextmanager
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Simulation
try:
    world = WorldEngine(num_agents=10)
    logger.info("World Initialized Successfully")
except Exception as e:
    logger.error(f"World Init Failed: {e}")
    traceback.print_exc()

SIMULATION_TICK_RATE = 0.5 # 0.5s per tick = fluid movement

# --- Background Task ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

async def run_simulation():
    logger.info("Starting Simulation Loop...")
    while True:
        try:
            world.update()
            state = world.get_state()
            json_state = json.dumps(state)
            await manager.broadcast(json_state)
        except Exception as e:
            logger.error(f"Simulation Loop Error: {e}")
            traceback.print_exc()
        
        await asyncio.sleep(SIMULATION_TICK_RATE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(run_simulation())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/map")
async def get_map():
    return world.get_map()

@app.get("/debug/state")
async def get_state():
    return world.get_state()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
