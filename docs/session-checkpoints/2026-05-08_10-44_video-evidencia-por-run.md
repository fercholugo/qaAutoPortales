# Checkpoint: video-evidencia-por-run — 2026-05-08 10:44

## Estado del contexto
Mensajes restantes estimados: ~10 (Urgente)
Intercambios en esta sesión: ~35 rondas
Tipo de sesión: Pesada (múltiples archivos, pruebas en vivo, agentes)

## Objetivo de la sesión
Implementar interfaz web FastAPI para ejecutar tests de portales cautivos con streaming en vivo, historial SQLite y evidencia de video por ejecución. Deploy en Railway.

## Contexto del proyecto
Proyecto: qa-auto-portales — QA automation (Python, Selenium, pytest-bdd, Screenplay)
Directorio: /Users/fernandolugo/code/qa-auto-portales/
Rama activa: **feature/web-interface**
Servidor local: `uvicorn server.main:app --host 0.0.0.0 --port 8000` (puede estar corriendo)

## Archivos relevantes

### Implementados y commiteados (feature/web-interface)
- `server/main.py` — FastAPI: endpoints REST + WebSocket
- `server/database.py` — SQLite async: tabla `runs`
- `server/runner.py` — subprocess executor con streaming
- `server/portales.json` — 3 portales reales: Bancolombia, Bancoagrario, Centros Digitales
- `server/static/index.html` — UI completa
- `tests/test_steps_portal_cautivo_normal_flujo_principal.py` — lee `PORTAL_URL` env var (línea 30)
- `requirements.txt` — fastapi, uvicorn, aiosqlite agregados

### Sin commitear
- `reporte_html/qa_history.db` — DB SQLite generada en ejecución
- `reporte_html/runs/` — reportes por run_id generados

## Progreso

### Completado
- [x] Fase 0: git (commit main + rama feature/web-interface)
- [x] Fase 1: Backend FastAPI completo (endpoints, SQLite, runner subprocess)
- [x] Fase 2: UI HTML (dropdown portales reales, terminal en vivo, historial)
- [x] URL dinámica: PORTAL_URL env var → test usa la URL seleccionada en UI
- [x] portales.json actualizado con 3 portales reales y nombres descriptivos
- [x] Probado en vivo: UI funciona, tests corren, streaming funciona, historial se guarda

### Pendiente — PRÓXIMO PASO (esperando autorización)

**Video de evidencia por ejecución — 4 cambios acordados:**

**Cambio 1 — `server/database.py`**
- Agregar columna `ruta_video TEXT` a la tabla `runs`
- Migración: `ALTER TABLE runs ADD COLUMN ruta_video TEXT` con try/except para DB existente
- Actualizar `actualizar_run()` para recibir y guardar `ruta_video`

**Cambio 2 — `tests/test_steps_portal_cautivo_normal_flujo_principal.py`**
```python
# Reemplazar bloque de video (líneas ~39-48):
videos_dir = os.getenv("VIDEO_DIR", "reporte_html/videos_ejecuciones")
os.makedirs(videos_dir, exist_ok=True)
video_path = os.path.join(
    videos_dir,
    "evidencia.mp4" if os.getenv("VIDEO_DIR") else f"{alias}_{keyword}_{ts}.mp4"
)
```
- CLI: video en `reporte_html/videos_ejecuciones/{alias}_{keyword}_{ts}.mp4` (sin cambio)
- Web UI: video en `reporte_html/runs/{run_id}/evidencia.mp4` (mismo dir que reporte)

**Cambio 3 — `server/runner.py`**
- Agregar al env del subprocess:
  ```python
  "RECORD_VIDEO": "1",
  "VIDEO_INTERVAL": "0.3",
  "VIDEO_DIR": f"reporte_html/runs/{run_id}",
  ```
- Después de terminar el test, pasar `ruta_video = f"runs/{run_id}/evidencia.mp4"` a `actualizar_run()`
- Actualizar firma de `actualizar_run()` en la llamada

**Cambio 4 — `server/static/index.html`**
- En la tabla de historial, mostrar link de video cuando `r.ruta_video` exista:
  ```html
  ${r.ruta_video ? `<a class="report-btn" href="/reportes/${r.ruta_video}" target="_blank">▶ Video</a>` : '—'}
  ```

## Estructura objetivo por ejecución
```
reporte_html/runs/{run_id}/
├── reporte.html     ← ya implementado
└── evidencia.mp4   ← pendiente con estos 4 cambios
```

## Decisiones tomadas
1. Nombre fijo `evidencia.mp4` para runs desde web (predictable, un solo video por run)
2. CLI mantiene nombre con timestamp (sin cambio al flujo existente)
3. `VIDEO_DIR` env var en lugar de hardcodear — backwards compatible
4. `ruta_video` en DB para mostrar en historial y link directo

## Pendiente posterior a video
- [ ] Fase 3: Actualizar Dockerfile (CMD → uvicorn, EXPOSE 8000)
- [ ] Fase 3: Actualizar docker-compose.yml (puerto 8000:8000)
- [ ] Probar con docker-compose up --build
- [ ] Agregar reporte_html/runs/ y qa_history.db a .gitignore
- [ ] Fase 4: Deploy en Railway (volumen persistente para reporte_html/)

## Problemas conocidos
- Portal `2cc81ba2565e` (Centros Digitales): falla con "Paneles encontrados: 0" — portal posiblemente inactivo o con estructura diferente. No es bug de la UI.
- La URL final de Centros Digitales no está en `IsOnExpectedUrl.VALID_URLS` — pendiente agregar cuando se sepa la URL de redirect correcta.
