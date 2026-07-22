# Checkpoint: railway-deploy-github-push — 2026-07-09 13:42

## Estado del contexto
Mensajes restantes estimados: ~3 (Urgente)
Intercambios en esta sesión: ~38
Tipo de sesión: Pesada (ediciones de código, commits, configuración de deploy)

## Objetivo de la sesión
Desplegar el proyecto qa-auto-portales en Railway. El código ya está en Bitbucket; se creó un repo en GitHub como puente para conectar con Railway (que no soporta Bitbucket nativamente).

## Contexto del proyecto
Proyecto: qa-auto-portales — QA automation (Python, Selenium, pytest-bdd, Screenplay)
Directorio: /Users/fernandolugo/code/qa-auto-portales/
Branch activo: feature/web-interface
Último commit: `4c210e0` — [NEW] Add web interface with history, per-portal results and Railway deploy config

## Archivos relevantes en esta sesión
- `Dockerfile` — CMD: `uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8000}` (Railway compatible)
- `.dockerignore` — excluye reporte_html/, allure-report/, docs/session-checkpoints/
- `server/static/index.html` — UI simplificada sin selector único/varios ni output card
- `server/runner.py` — siempre batch; rastrea resultados por portal
- `server/database.py` — columna `resultados` JSON por portal

## Progreso

### Completado
- [x] Dockerfile actualizado para Railway (CMD con uvicorn + PORT)
- [x] .dockerignore actualizado
- [x] Commit y push a Bitbucket (branch feature/web-interface)
- [x] Repo GitHub creado: github.com/ferchoulugo/qaAutoPortales (público)
- [x] Railway conectado al repo GitHub ferchoulugo/qaAutoPortales, branch main
- [x] Remote github agregado localmente: `git remote add github https://github.com/ferchoulugo/qaAutoPortales.git`

### En curso
- [ ] Push del código a GitHub — bloqueado por autenticación

### Pendiente
- [ ] **Resolver autenticación GitHub para push**: GitHub no acepta contraseña por HTTPS. Opciones:
  - **Opción A (recomendada)**: Personal Access Token → GitHub Settings → Developer settings → Tokens (classic) → scope `repo` → usar: `git push https://TOKEN@github.com/ferchoulugo/qaAutoPortales.git feature/web-interface:main`
  - **Opción B**: SSH key → `git remote set-url github git@github.com:ferchoulugo/qaAutoPortales.git` → `git push github feature/web-interface:main`
- [ ] Una vez pusheado: Railway detecta el push y hace build automático
- [ ] Verificar que el build pase (Dockerfile instala Chrome, Python deps, arranca uvicorn)
- [ ] Configurar dominio público en Railway: Settings → Networking → Generate Domain
- [ ] Agregar volumen persistente: Settings → Volumes → Add Volume → Mount Path: `/app/reporte_html`

## Decisiones técnicas tomadas
1. **GitHub como puente**: Railway no soporta Bitbucket nativamente — se creó repo GitHub separado. Bitbucket sigue siendo el origin principal.
2. **Push feature/web-interface como main en GitHub**: Railway está configurado en branch `main`; se hace `git push github feature/web-interface:main` para que coincida.
3. **Volumen en /app/reporte_html**: SQLite (`qa_history.db`) y reportes viven ahí — sin volumen se pierden en cada redeploy.
4. **Chrome headless automático**: `src/abilities/browse_the_web.py` detecta `/.dockerenv` y activa `--headless --no-sandbox --disable-dev-shm-usage`. Railway corre Docker, funciona sin cambios.

## Problemas / Bloqueos conocidos
- **Push a GitHub falla**: `fatal: repository not found` — en realidad es error de autenticación. GitHub requiere Personal Access Token (no contraseña) para HTTPS. El remote está bien configurado.
- **Railway muestra "Connected branch does not exist"**: porque el repo GitHub está vacío. Se resuelve al hacer el push exitoso.

## Remotes configurados localmente
```
origin  → https://fernandolugo1@bitbucket.org/repo-datawifi/automated_testing.git
github  → https://github.com/ferchoulugo/qaAutoPortales.git
```

## Cambios sin commitear
```
?? docs/session-checkpoints/2026-07-09_13-20_railway-deploy-setup.md
?? reporte_html/qa_history.db   ← no commitear
?? reporte_html/runs/           ← no commitear
```
