"""Gestión de la base de datos SQLite para historial de ejecuciones."""

import aiosqlite
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "reporte_html" / "qa_history.db"
COLOMBIA_TZ = timezone(timedelta(hours=-5))


async def init_db():
    """Crea la tabla de runs si no existe."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id           TEXT PRIMARY KEY,
                fecha        TEXT NOT NULL,
                portal_id    TEXT NOT NULL,
                portal_nombre TEXT NOT NULL,
                escenario    TEXT NOT NULL,
                estado       TEXT NOT NULL DEFAULT 'running',
                ruta_reporte TEXT,
                ruta_video   TEXT,
                duracion_seg REAL,
                log          TEXT,
                resultados   TEXT
            )
        """)
        for col in ("ruta_video", "resultados"):
            try:
                await db.execute(f"ALTER TABLE runs ADD COLUMN {col} TEXT")
            except Exception:
                pass  # columna ya existe
        await db.commit()


async def crear_run(portal_id: str, portal_nombre: str, escenario: str) -> str:
    """Inserta un nuevo run con estado 'running' y retorna su ID."""
    run_id = str(uuid.uuid4())[:8]
    fecha = datetime.now(COLOMBIA_TZ).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO runs (id, fecha, portal_id, portal_nombre, escenario, estado) "
            "VALUES (?, ?, ?, ?, ?, 'running')",
            (run_id, fecha, portal_id, portal_nombre, escenario)
        )
        await db.commit()
    return run_id


async def actualizar_run(
    run_id: str,
    estado: str,
    ruta_reporte: str | None,
    duracion_seg: float,
    log: str,
    ruta_video: str | None = None,
    resultados: str | None = None,
):
    """Actualiza estado, rutas, duración, log y resultados por portal."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE runs SET estado=?, ruta_reporte=?, ruta_video=?, duracion_seg=?, log=?, resultados=? WHERE id=?",
            (estado, ruta_reporte, ruta_video, duracion_seg, log, resultados, run_id)
        )
        await db.commit()


async def listar_runs(limit: int = 20):
    """Retorna las últimas N ejecuciones ordenadas por fecha descendente."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, fecha, portal_nombre, escenario, estado, ruta_reporte, ruta_video, duracion_seg, resultados "
            "FROM runs ORDER BY fecha DESC LIMIT ?",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def obtener_run(run_id: str):
    """Retorna un run por su ID, o None si no existe."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM runs WHERE id=?", (run_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
