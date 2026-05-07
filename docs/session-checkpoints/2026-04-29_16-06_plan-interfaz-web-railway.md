# Checkpoint: plan-interfaz-web-railway — 2026-04-29 16:06

## Estado del contexto
Mensajes restantes estimados: ~8 (Urgente)
Intercambios en esta sesión: ~20 rondas
Tipo de sesión: Pesada (múltiples subagentes, planificación extensa, escritura de archivos)

## Objetivo de la sesión
Diseñar e implementar una interfaz web para el proyecto qa-auto-portales que permita:
1. Seleccionar portales desde un dropdown, escoger escenario (único/varios) y ejecutar tests con un botón
2. Ver el output en vivo durante la ejecución (WebSocket)
3. Acceder al reporte HTML generado al terminar
4. Guardar historial de ejecuciones en SQLite
5. Desplegar todo en Railway con Docker existente

**La implementación NO ha comenzado aún.** Solo se definió el plan.

## Contexto del proyecto
Proyecto: qa-auto-portales — QA automation (Python, Selenium, pytest-bdd, Screenplay)
Directorio: /Users/fernandolugo/code/qa-auto-portales/
Rama actual: main (trabajo nuevo irá en `feature/web-interface`)

## Decisiones de diseño ya acordadas
1. **FastAPI** como backend (Python, async, WebSocket para streaming)
2. **SQLite** para historial (sin servicios externos, archivo en volumen Railway)
3. **HTML + JS vanilla** para la UI (sin frameworks)
4. **portales.json** para lista de URLs configurables (no en DB)
5. **Sin autenticación** por ahora
6. **Railway** como plataforma de deploy (Docker ya configurado)
7. **No tocar** `src/`, `tests/`, `features/`, `conftest.py`, `run_tests.sh`

## Archivos relevantes en esta sesión

### Creados en esta sesión
- `CLAUDE.md` — instrucciones automáticas del proyecto (auto-carga de checkpoints + reglas de trabajo)
- `~/.claude/commands/save-session.md` — comando global `/save-session`
- `docs/session-checkpoints/` — directorio de checkpoints

### Archivos base del proyecto (referencia)
- `Dockerfile` — ya tiene Chrome headless, solo cambiar CMD a uvicorn
- `docker-compose.yml` — agregar puerto 8000
- `requirements.txt` — agregar fastapi, uvicorn, aiosqlite
- `run_tests.sh` — script existente que el backend invocará como subprocess

## Progreso

### Completado
- [x] Implementar skill `/save-session` con frases naturales
- [x] Crear `CLAUDE.md` con auto-carga de checkpoints
- [x] Diseñar arquitectura completa de la interfaz web
- [x] Definir las 4 fases de implementación
- [x] Documentar todos los archivos a crear/modificar

### En curso
- [ ] Ninguna tarea en curso — todo pendiente de implementación

### Pendiente (en orden)
- [ ] **Fase 0**: Commitear `CLAUDE.md` + cambios pendientes en `main`, crear rama `feature/web-interface`
- [ ] **Fase 1**: Crear `server/main.py`, `server/database.py`, `server/runner.py`, `server/portales.json`
  - Agregar a `requirements.txt`: `fastapi>=0.110.0`, `uvicorn[standard]>=0.27.0`, `aiosqlite>=0.20.0`
- [ ] **Fase 2**: Crear `server/static/index.html` (dropdown portales, selector único/varios, botón, panel output, historial)
- [ ] **Fase 3**: Actualizar `Dockerfile` (CMD → uvicorn) y `docker-compose.yml` (puerto 8000)
- [ ] **Fase 4**: Probar con `docker-compose up --build` → `http://localhost:8000`
- [ ] **Fase 5**: Deploy en Railway (conectar repo, volumen persistente, variables de entorno)

## Plan detallado
El plan completo está guardado en:
`~/.claude/plans/necesito-implementar-una-skill-indexed-spark.md`

### Estructura de archivos a crear
```
server/
├── main.py          ← FastAPI: endpoints + WebSocket
├── database.py      ← SQLite: tabla runs (id, fecha, portales, escenario, estado, ruta_reporte, duracion_seg)
├── runner.py        ← subprocess de run_tests.sh + captura stdout para WebSocket
├── portales.json    ← lista de portales configurables
└── static/
    └── index.html   ← UI completa en un solo archivo
```

### Endpoints FastAPI
- `GET /` → index.html
- `GET /portales` → portales.json
- `POST /run` → inicia test, retorna run_id
- `WS /live/{run_id}` → streaming stdout en tiempo real
- `GET /status/{run_id}` → estado del run
- `GET /history` → historial SQLite
- `GET /report/{run_id}` → sirve HTML del reporte

## Problemas / Bloqueos conocidos
- Ninguno identificado aún

## Cambios sin commitear
```
 M features/portal_cautivo_normal_flujo_principal.feature
 M src/questions/is_on_expected_url.py
?? CLAUDE.md
?? docs/session-checkpoints/
```

Estos cambios deben commitearse en `main` antes de crear la rama `feature/web-interface`.

## Para retomar
Al iniciar nueva conversación, CLAUDE.md cargará este checkpoint automáticamente.
Primera acción: Fase 0 — commitear los cambios pendientes en main y crear la rama feature/web-interface.
