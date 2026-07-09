# Checkpoint: web-interface-url-dropdown — 2026-05-07 17:15

## Estado del contexto
Mensajes restantes estimados: ~8 (Urgente)
Intercambios en esta sesión: ~30 rondas
Tipo de sesión: Pesada (múltiples archivos creados, subagentes, pruebas en vivo)

## Objetivo de la sesión
Implementar interfaz web (FastAPI + SQLite + HTML) para ejecutar tests de portales cautivos desde una URL, con streaming en vivo del output y historial de ejecuciones. Despliegue en Railway.

## Contexto del proyecto
Proyecto: qa-auto-portales — QA automation (Python, Selenium, pytest-bdd, Screenplay)
Directorio: /Users/fernandolugo/code/qa-auto-portales/
Rama activa: **feature/web-interface**

## Archivos relevantes en esta sesión

### Creados (nuevos en feature/web-interface)
- `server/main.py` — FastAPI: endpoints REST + WebSocket streaming
- `server/database.py` — SQLite async (aiosqlite): tabla `runs` con historial
- `server/runner.py` — Subprocess executor: lanza pytest, captura stdout línea a línea
- `server/portales.json` — Lista de portales (PENDIENTE actualizar con URLs reales)
- `server/static/index.html` — UI completa: dropdown, selector único/varios, terminal en vivo, historial
- `server/__init__.py` — Módulo Python

### Modificados
- `requirements.txt` — Agregado: fastapi, uvicorn[standard], aiosqlite

### Sin commitear (archivos generados en ejecución)
- `reporte_html/qa_history.db` — SQLite DB generada al arrancar el servidor
- `reporte_html/runs/` — Directorio de reportes por run_id

## Progreso

### Completado
- [x] Fase 0: Commit en main + rama `feature/web-interface` creada
- [x] Fase 1: Backend FastAPI (main.py, database.py, runner.py, portales.json)
- [x] Fase 2: UI HTML completa (index.html) — probada en vivo en http://localhost:8000
- [x] Servidor arranca correctamente, endpoints `/portales`, `/history`, `/` funcionan
- [x] Dependencias instaladas en venv

### En curso — BLOQUEADO esperando confirmación
- [ ] **Actualizar dropdown para mostrar URLs individuales de portales** (no tipos Portal Normal/API)

  **Problema identificado:** El dropdown muestra "Portal Cautivo Normal" / "Portal Cautivo API" (tipos de portal), pero el usuario quiere ver las URLs individuales del `Examples` del feature file.

  **Solución acordada — 3 cambios pendientes de confirmación:**

  **Cambio 1 — `tests/test_steps_portal_cautivo_normal_flujo_principal.py` línea 30:**
  ```python
  # Agregar DESPUÉS de la firma del step (línea 30), ANTES de form_data:
  url = os.getenv("PORTAL_URL", url)  # override desde web UI si está definida
  form_data = {"url": url}
  ```

  **Cambio 2 — `server/portales.json`** — reemplazar con URLs individuales:
  ```json
  [
    { "id": "p_764",  "nombre": "Portal 764x3806",     "url": "https://app.datawifi.co/easyfi/web/app.php/portal?called=764x3806&mac=",     "feature_alias": "portal_normal" },
    { "id": "p_54a",  "nombre": "Portal 54a274105f40", "url": "https://app.datawifi.co/easyfi/web/app.php/portal?called=54a274105f40&mac=", "feature_alias": "portal_normal" },
    { "id": "p_285",  "nombre": "Portal 28534eae4400", "url": "https://app.datawifi.co/easyfi/web/app.php/portal?called=28534eae4400&mac=", "feature_alias": "portal_normal" }
  ]
  ```
  *(Nombres descriptivos reales pendientes — el usuario los confirmará)*

  **Cambio 3 — `server/runner.py`** — pasar `PORTAL_URL` al subprocess:
  En `ejecutar_test()`, agregar al dict `env`:
  ```python
  if escenario == "unico" and portal_url:
      env["PORTAL_URL"] = portal_url
  ```
  Y actualizar `ejecutar_test()` para recibir `portal_url` como parámetro.

  **Cambio 4 — `server/main.py`** — pasar `url` del portal al runner:
  En `POST /run`, obtener `portal["url"]` y pasarlo a `runner.ejecutar_test()`

### Pendiente
- [ ] Confirmar nombres reales de los portales para portales.json
- [ ] Aplicar los 4 cambios de la URL dinámica (pendiente autorización usuario)
- [ ] Fase 3: Actualizar Dockerfile (CMD → uvicorn, puerto 8000)
- [ ] Fase 3: Actualizar docker-compose.yml (puerto 8000:8000)
- [ ] Probar con docker-compose up --build localmente
- [ ] Fase 4: Deploy en Railway

## Decisiones técnicas tomadas
1. **No agregar `nombre_portal` a la tabla `Examples` del feature file**: pytest-bdd puede fallar con columnas sin placeholder en los steps. Los nombres viven solo en portales.json.
2. **`os.getenv("PORTAL_URL", url)`**: compatibilidad total con ejecución CLI — si PORTAL_URL no está definida, usa la URL del feature file. Cero impacto en flujo existente.
3. **`varios` usa la tabla `Examples` del feature file**: fuente de verdad para múltiples portales en CLI y en web. `portales.json` es fuente de verdad para el dropdown.
4. **SQLite en `/reporte_html/qa_history.db`**: persiste en el volumen Railway junto con los reportes.
5. **Reportes por run_id en `reporte_html/runs/{run_id}/reporte.html`**: evita sobreescribir entre ejecuciones concurrentes.

## Arquitectura web implementada
```
GET  /           → index.html
GET  /portales   → portales.json
POST /run        → lanza pytest en background, retorna run_id
WS   /live/{id}  → streaming stdout tiempo real
GET  /status/{id}→ estado del run (SQLite)
GET  /history    → últimas 20 ejecuciones
GET  /report/{id}→ sirve HTML del reporte
```

## Problemas / Bloqueos conocidos
- `reporte_html/qa_history.db` y `reporte_html/runs/` no están en .gitignore — agregar antes del deploy
- El servidor actual corre en puerto 8000 localmente (puede seguir corriendo)

## Cambios sin commitear
```
?? reporte_html/qa_history.db
?? reporte_html/runs/
```
(archivos generados, no código — no es urgente commitearlos)

## Para retomar
Primera acción: preguntar al usuario los nombres descriptivos para los 3 portales en portales.json, luego aplicar los 4 cambios de la URL dinámica con su autorización.
