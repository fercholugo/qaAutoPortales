"""Ejecuta los tests de pytest como subprocess y transmite el output en tiempo real."""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_DIR = Path(__file__).parent.parent

# Almacén en memoria por run_id: líneas capturadas y cola para streaming
output_store: Dict[str, List[str]] = {}
output_queues: Dict[str, asyncio.Queue] = {}

FEATURE_MAP = {
    "portal_normal": {
        "steps":   "tests/test_steps_portal_cautivo_normal_flujo_principal.py",
        "feature": "features/portal_cautivo_normal_flujo_principal.feature",
    },
    "portal_api": {
        "steps":   "tests/test_steps_portal_cautivo_normal_flujo_principal.py",
        "feature": "features/portal_cautivo_api_flujo_principal.feature",
    },
}


def _aplicar_personalizacion(report_path: Path):
    """Importa y aplica las transformaciones de personalizar_reporte.py al reporte generado."""
    try:
        if str(PROJECT_DIR) not in sys.path:
            sys.path.insert(0, str(PROJECT_DIR))
        from reporte_html.personalizar_reporte import (
            eliminar_log_vacio,
            mover_environment_despues_de_resultados,
            agregar_js_ocultar_log,
        )
        eliminar_log_vacio(str(report_path))
        mover_environment_despues_de_resultados(str(report_path))
        agregar_js_ocultar_log(str(report_path))
    except Exception as e:
        print(f"[Runner] Personalización omitida: {e}")


async def ejecutar_test(run_id: str, feature_alias: str, escenario: str):
    """
    Lanza pytest en background, captura stdout línea a línea,
    actualiza SQLite al terminar y señala fin del stream.
    """
    from server import database

    output_store[run_id] = []
    output_queues[run_id] = asyncio.Queue()

    async def _emit(line: str):
        output_store[run_id].append(line)
        await output_queues[run_id].put(line)

    if feature_alias not in FEATURE_MAP:
        await _emit(f"[Error] Feature alias no reconocido: {feature_alias}\n")
        await output_queues[run_id].put(None)
        await database.actualizar_run(run_id, "error", None, 0, "".join(output_store[run_id]))
        return

    info = FEATURE_MAP[feature_alias]
    report_dir = PROJECT_DIR / "reporte_html" / "runs" / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "reporte.html"

    cmd = [
        sys.executable, "-m", "pytest",
        info["steps"], "-v", "-s",
        f"--html={report_path}",
        "--self-contained-html",
    ]
    if escenario:
        cmd.extend(["-k", escenario])

    env = {
        **os.environ,
        "FEATURE_ALIAS": feature_alias,
        "SCENARIO_KEYWORD": escenario or "",
    }

    await _emit(f"[QA Runner] Portal: {feature_alias} | Escenario: {escenario or 'todos'}\n")
    await _emit(f"[QA Runner] Comando: {' '.join(cmd[2:])}\n\n")

    inicio = time.time()
    estado = "error"

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
            cwd=str(PROJECT_DIR),
        )
        async for raw in proc.stdout:
            await _emit(raw.decode("utf-8", errors="replace"))

        await proc.wait()
        estado = "done" if proc.returncode == 0 else "error"

    except Exception as e:
        await _emit(f"[Error crítico] {e}\n")

    duracion = round(time.time() - inicio, 1)
    await _emit(f"\n[QA Runner] Finalizado — Estado: {estado.upper()} ({duracion}s)\n")

    ruta_relativa: Optional[str] = None
    if report_path.exists():
        _aplicar_personalizacion(report_path)
        ruta_relativa = f"runs/{run_id}/reporte.html"
        await _emit(f"[QA Runner] Reporte disponible: /reportes/{ruta_relativa}\n")

    log_completo = "".join(output_store[run_id])
    await database.actualizar_run(run_id, estado, ruta_relativa, duracion, log_completo)

    # Señal de fin de stream para el WebSocket
    await output_queues[run_id].put(None)
