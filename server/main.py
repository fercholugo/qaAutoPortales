"""Servidor FastAPI: endpoints REST + WebSocket para QA Auto Portales."""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import database, runner

BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
REPORTE_DIR = PROJECT_DIR / "reporte_html"
PORTALES_FILE = BASE_DIR / "portales.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    yield


app = FastAPI(title="QA Auto Portales", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/reportes", StaticFiles(directory=str(REPORTE_DIR)), name="reportes")


class RunRequest(BaseModel):
    portal_id: str
    escenario: str = "unico"


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/portales")
async def get_portales():
    with open(PORTALES_FILE, encoding="utf-8") as f:
        return json.load(f)


@app.post("/run")
async def run_test(body: RunRequest, background_tasks: BackgroundTasks):
    with open(PORTALES_FILE, encoding="utf-8") as f:
        portales = json.load(f)

    portal = next((p for p in portales if p["id"] == body.portal_id), None)
    if not portal:
        raise HTTPException(status_code=400, detail="Portal no encontrado")

    run_id = await database.crear_run(body.portal_id, portal["nombre"], body.escenario)
    background_tasks.add_task(
        runner.ejecutar_test, run_id, portal["feature_alias"], body.escenario
    )
    return {"run_id": run_id, "estado": "running"}


@app.websocket("/live/{run_id}")
async def websocket_live(websocket: WebSocket, run_id: str):
    await websocket.accept()

    # Espera hasta 5s a que el runner registre el run_id
    for _ in range(50):
        if run_id in runner.output_queues:
            break
        await asyncio.sleep(0.1)

    if run_id not in runner.output_queues:
        await websocket.close()
        return

    # Reproduce líneas ya capturadas antes de que el WS conectara
    for line in runner.output_store.get(run_id, []):
        try:
            await websocket.send_text(line)
        except Exception:
            return

    # Transmite nuevas líneas hasta señal de fin (None)
    q = runner.output_queues[run_id]
    while True:
        try:
            line = await asyncio.wait_for(q.get(), timeout=300)
            if line is None:
                break
            await websocket.send_text(line)
        except asyncio.TimeoutError:
            break
        except WebSocketDisconnect:
            return

    try:
        await websocket.close()
    except Exception:
        pass


@app.get("/status/{run_id}")
async def get_status(run_id: str):
    run = await database.obtener_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run no encontrado")
    return run


@app.get("/history")
async def get_history():
    return await database.listar_runs()
