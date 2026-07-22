# 🚀 QA Auto Portales - Framework de Automatización

## 🌐 Interfaz Web

Además de la ejecución por CLI, el proyecto tiene una interfaz web (FastAPI) que permite lanzar pruebas desde el navegador, sin necesidad de tocar la terminal:

- Selector de portal(es) a probar (checkboxes, con búsqueda).
- Botón **"Ejecutar prueba"** que lanza el/los test(s) en background.
- **Historial de ejecuciones**: fecha, portal, estado (OK/FALLO), duración, y links al reporte HTML y al video de evidencia — persistente entre ejecuciones.
- Salida en vivo del test mientras corre (streaming vía WebSocket).

Para correrla en local:
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

---

## ☁️ Despliegue en producción (Railway)

El proyecto está desplegado en Railway y accesible públicamente vía navegador, sin que nadie necesite tener el repo clonado.

**Cómo está armado:**
- El código fuente vive en Bitbucket; un repo puente en GitHub conecta con Railway (que no soporta Bitbucket nativamente).
- `Dockerfile` empaqueta Python 3.12 + Chromium + ChromeDriver + todas las dependencias.
- **Región**: US East (Virginia) — la más cercana/rápida disponible hacia Colombia (Railway no tiene región en Latinoamérica).
- **Volumen persistente** montado en `/app/reporte_html`: el historial de ejecuciones y los reportes/videos sobreviven a cada redeploy.
- La hora del historial se registra en horario de Colombia (no UTC).

**El reto técnico principal que se resolvió:** Chrome/Selenium fallaba consistentemente al arrancar en el contenedor de Railway (`DevToolsActivePort file doesn't exist`). La causa raíz: el código detectaba si estaba "en Docker" verificando la existencia de `/.dockerenv`, pero ese archivo no existe en el runtime real de Railway (aunque sí en su consola interactiva) — por lo que el navegador headless nunca se configuraba correctamente. Se corrigió:
1. Detectando el entorno Docker por la presencia del binario de `chromedriver`, no de `/.dockerenv`.
2. Lanzando ChromeDriver como proceso independiente en vez de dejar que Selenium lo gestione internamente (más estable en este entorno).
3. Agregando esperas explícitas donde la latencia de red (mayor en la nube que en local) hacía que el detector de elementos llegara demasiado rápido.

---

## 🧠 Skill de mantenimiento de portales (`actualizar-portal`)

Los portales cautivos cambian su interfaz con el tiempo (nuevas versiones, nuevos proveedores de red, elementos publicitarios, etc.), lo que puede romper la detección automática. Para mantener esto sin perder tiempo redescubriendo el mismo proceso cada vez, se creó un **skill de Claude Code** (`.claude/skills/actualizar-portal/`) — una guía de diagnóstico, **no un componente que participe en la ejecución de los tests**. La automatización sigue siendo 100% determinista; el skill es solo una ayuda de desarrollo.

**Qué hace:**
- Si el portal es nuevo, ayuda a agregarlo a `server/portales.json`.
- Corre (o localiza) una ejecución de prueba y analiza la evidencia real generada (HTML de la página, video, reporte) para entender qué cambió.
- Distingue entre un **bug de código** (falta lógica de detección, corregible) y un **problema del propio portal** (ej. error de configuración de red, fuera de alcance del código).
- Propone el ajuste mínimo al código, siempre mostrando el diff exacto y esperando confirmación antes de aplicarlo.
- Mantiene una lista de "lecciones aprendidas" con los casos ya resueltos, para no repetir el mismo proceso de prueba y error.

Se activa con frases como `"sk actualizar portal X"`, `"sk agregar portal X"`, `"sk portal falla X"`, o simplemente describiendo el problema en lenguaje natural.

**Estado actual de los portales** (validados en producción):
| Portal | Estado |
|---|---|
| Bancoagrario | ✅ OK |
| Bancolombia | ✅ OK |
| Santander México | ✅ OK |
| Sitwifi | ✅ OK |
| Centros Digitales | ✅ OK |

---
## 🔀 Interfaz web o consola — ambas opciones siguen disponibles

La interfaz web no reemplaza la ejecución por consola — es una capa adicional sobre el mismo `pytest` / `run_tests.sh` que ya existía. Podés seguir corriendo las pruebas exactamente igual que antes, tanto en local como dentro del contenedor Docker.

**Por consola, según el escenario:**

Primero activar el entorno:
```bash
source venv/bin/activate
```

```bash
# Escenario "unico" — un solo portal (el definido en el Scenario del feature)
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal unico

# Escenario "varios" — múltiples portales (la tabla Examples del feature)
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal varios
```

**Por interfaz web:** seleccionás uno o varios portales desde los checkboxes y le das a "Ejecutar prueba" — internamente arma y corre el mismo comando de `pytest` por cada portal seleccionado.

---
**Desarrollado con Python + Selenium + pytest-bdd**
