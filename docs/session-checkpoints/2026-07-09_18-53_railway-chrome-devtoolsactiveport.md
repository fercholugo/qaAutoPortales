# Checkpoint: railway-chrome-devtoolsactiveport — 2026-07-09 18:53

## Estado del contexto
Mensajes restantes estimados: ~0 (Urgente)
Intercambios en esta sesión: ~55+ (sesión muy larga y pesada, con múltiples redeploys y screenshots)
Tipo de sesión: Pesada (debugging profundo, muchas ediciones de código, muchos redeploys a Railway)

## Objetivo de la sesión
Continuación del despliegue en Railway (ver checkpoints previos `2026-07-09_13-20` y `2026-07-09_13-42`). Una vez desplegada la web, el bloqueante principal fue que **Chrome/Selenium nunca lograba arrancar** en el contenedor de Railway al ejecutar un test real, con el error persistente `WebDriverException: unknown error: Chrome failed to start: exited abnormally. (DevToolsActivePort file doesn't exist)`.

## Contexto del proyecto
Proyecto: qa-auto-portales — QA automation (Python, Selenium, pytest-bdd, Screenplay)
Directorio: /Users/fernandolugo/code/qa-auto-portales/
Branch activo: feature/web-interface
Deploy: Railway, servicio `qaAutoPortales`, repo puente en GitHub `fercholugo/qaAutoPortales` (branch main), Railway conectado ahí. Bitbucket sigue siendo el origin real pero NO se ha sincronizado con los últimos commits de esta sesión (ver "Cambios sin commitear" más abajo — realmente son commits locales que sí están en `feature/web-interface` pero pendientes de push a Bitbucket).

## Archivos relevantes en esta sesión
- `src/abilities/browse_the_web.py` — el archivo central del bloqueante. Reescrito varias veces en esta sesión (ver Decisiones técnicas).
- `server/runner.py` — se le agregó `print(line, end="", flush=True)` dentro de `_emit()` para que la salida del subprocess de pytest también aparezca en los Deploy Logs de Railway (antes solo iba al WebSocket).
- `server/static/index.html` — se agregó de vuelta (temporalmente) una caja "Salida en vivo" (`#live-output-section` / `#live-output`) que muestra el stream del WebSocket mientras corre un test. Se puede quitar cuando ya no se necesite para diagnóstico.
- `docs/session-checkpoints/2026-07-09_13-42_railway-deploy-github-push.md` y `2026-07-09_13-20_railway-deploy-setup.md` — checkpoints previos de esta misma cadena de trabajo.

## Progreso

### Completado
- [x] Repo GitHub conectado a Railway, deploy funcionando, dominio público generado (`qaautoportales-production.up.railway.app`).
- [x] Fix WebSocket `ws://` → `wss://` dinámico (mixed content bloqueaba la actualización automática de la UI). Confirmado funcionando.
- [x] `PYTHONUNBUFFERED=1` agregado como variable de entorno en Railway para logs en tiempo real.
- [x] **Causa raíz encontrada del crash de Chrome**: el código usaba `os.path.exists('/.dockerenv')` para decidir si aplicar flags headless/no-sandbox. En el runtime real de Railway (que NO es Docker clásico, aparentemente usa otro mecanismo de contenedores — la Consola de Railway sí parece ser un contenedor Docker normal con `/.dockerenv`, pero el proceso real que sirve tráfico, NO), ese archivo no existe, así que el código SIEMPRE caía a la rama "local" (sin headless, sin `--no-sandbox`, sin `binary_location`), y Chrome intentaba arrancar en modo gráfico como root sin display — de ahí el crash. Cambiado a `os.path.exists(os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver"))`, que es una detección confiable independiente del entorno de ejecución.
- [x] Como medida adicional (workaround, no estrictamente necesaria tras el fix de arriba, pero ya probada y dejada en su lugar): en vez de dejar que Selenium `Service` gestione el lanzamiento de chromedriver, el código ahora lanza chromedriver como **proceso independiente** (`subprocess.Popen`) en el puerto 9515, espera a que responda en `/status`, y conecta con `webdriver.Remote(command_executor=...)` en vez de `webdriver.Chrome(service=...)`. Esto se demostró funcionar de forma consistente en pruebas manuales por consola, mientras que el enfoque `Service`-gestionado fallaba repetidamente sin causa raíz identificable (se investigó a fondo el mecanismo interno de `log_output`/`ChromiumService` de Selenium sin encontrar explicación satisfactoria — ver más abajo).
- [x] Bug introducido y corregido en la misma sesión: un `import time` local dentro de la rama `elif self.browser_name == "safari":` (código viejo, no tocado antes) hacía que Python tratara `time` como variable local de TODA la función `_init_driver`, rompiendo el nuevo `time.sleep(0.5)` del loop de espera de chromedriver con `UnboundLocalError`. Se quitó el import duplicado (ya existe `import time` a nivel de módulo).
- [x] Se agregó una caja de "Salida en vivo" en la UI (`server/static/index.html`) y se hizo que `runner.py` también imprima el output del subprocess a los Deploy Logs de Railway — esto fue clave para finalmente ver el error real (antes estábamos completamente ciegos ante el subprocess colgado/fallando, ya que su output solo iba al WebSocket, que la UI no mostraba, y Railway Console resultó ser un contenedor distinto al que sirve tráfico real).

### En curso
- [ ] **Validar que el fix funcione de punta a punta**. El último commit (`71cb6d0` — "Quitar import time duplicado...") se pusheó y se le pidió al usuario esperar el redeploy y volver a correr el test. **No se ha confirmado aún si el test corre exitosamente o si queda algún bloqueante adicional.** Este es el primer paso al retomar la sesión: pedir al usuario que corra el test de nuevo y comparta qué sale en la caja de "Salida en vivo".

### Pendiente
- [ ] Confirmar que un test corre exitosamente de principio a fin en Railway (arranca Chrome, navega el portal real, complete el flujo).
- [ ] Si funciona: considerar si vale la pena revertir el workaround de `webdriver.Remote()` + chromedriver standalone y volver al enfoque `Service`-gestionado ahora que el fix real (detección de Docker) está aplicado — o dejarlo así, ya que funciona y no hay urgencia de "limpiar". Se recomienda **dejarlo como está** salvo que cause problemas nuevos, para no reabrir esta investigación.
- [ ] Quitar (o dejar permanentemente, a decidir con el usuario) la caja de "Salida en vivo" agregada en `index.html` — fue pensada como ayuda de diagnóstico temporal.
- [ ] Configurar volumen persistente en Railway → Mount Path `/app/reporte_html` (pendiente desde checkpoints anteriores, para no perder historial SQLite y reportes en cada redeploy). Se intentó una vez a través del canvas de Railway pero se desvió hacia el "Agent" de Railway (asistente IA de pago) por accidente; no se completó.
- [ ] Sincronizar estos commits también a Bitbucket (origin), ya que solo se han pusheado a GitHub (puente hacia Railway) usando un Personal Access Token.
- [ ] **Revocar el Personal Access Token de GitHub** que el usuario compartió en el chat en texto plano en algún momento de esta sesión (quedó expuesto en el historial de conversación) y generar uno nuevo si se sigue necesitando — el usuario decidió seguir usándolo por ahora para no complicarse, pero sigue siendo buena práctica rotarlo.

## Decisiones técnicas tomadas
1. **No usar `/.dockerenv` para detectar entorno Docker**: no es confiable en el runtime de Railway. Se reemplazó por verificar la existencia del binario de chromedriver (`CHROMEDRIVER_BIN` env var o `/usr/bin/chromedriver` por defecto).
2. **Lanzar chromedriver como proceso independiente en vez de vía Selenium `Service`**: decisión pragmática tomada tras invertir mucho tiempo intentando diagnosticar por qué `Service`+`webdriver.Chrome()` fallaba consistentemente con "DevToolsActivePort file doesn't exist" mientras que chromedriver standalone (lanzado manualmente y conectado vía su API HTTP, o vía `webdriver.Remote()`) funcionaba siempre. No se encontró la causa raíz de esa discrepancia específica (se llegó a sospechar que era irrelevante una vez se corrigió el bug real de `/.dockerenv`, pero no se revirtió el workaround por prudencia — ya está probado que funciona).
3. **Reenviar el output del subprocess de pytest a los Deploy Logs de Railway** (`server/runner.py`): antes esa salida solo se guardaba para el WebSocket (que la UI no mostraba), dejándonos completamente ciegos ante fallos silenciosos. Ahora se ve en tiempo real tanto en Railway Deploy Logs como en la nueva caja de la UI.
4. **Se investigó pero no se resolvió del todo el misterio de `log_output` de Selenium** (por qué un archivo de log nunca se creaba ni con string ni con file object abierto directamente, incluso en pruebas aisladas de Python puro que deberían haber funcionado). Se abandonó esa línea de investigación en favor del workaround pragmático (ver punto 2) dado el tiempo ya invertido — probablemente relacionado con que la Consola de Railway corre en un contenedor distinto al que sirve tráfico real, aunque esto no explica del todo por qué tampoco funcionó en pruebas manuales *dentro* de la consola misma. Si se retoma esta investigación en el futuro, no es bloqueante para el proyecto.

## Problemas / Bloqueos conocidos
- **Railway Console ≠ contenedor que sirve tráfico real**: confirmado empíricamente (el traceback de un test real mostraba código que solo existe en la rama "else" de `_init_driver`, es decir `/.dockerenv` no existía ahí, mientras que en la Consola sí existía). Tener esto en cuenta para cualquier diagnóstico futuro vía Consola — lo que se prueba ahí no necesariamente refleja el comportamiento del proceso real.
- **Volumen persistente sin configurar**: cada redeploy borra el historial SQLite y los reportes generados en Railway.
- **Token de GitHub expuesto en el chat**: ver pendiente arriba.

## Cambios sin commitear
```
?? docs/session-checkpoints/2026-07-09_13-20_railway-deploy-setup.md
?? docs/session-checkpoints/2026-07-09_13-42_railway-deploy-github-push.md
?? reporte_html/qa_history.db   ← no commitear (datos locales)
?? reporte_html/runs/           ← no commitear (datos locales)
```
Todos los cambios de código de esta sesión (`browse_the_web.py`, `runner.py`, `index.html`) ya están commiteados localmente y pusheados a GitHub (`fercholugo/qaAutoPortales`, branch `main`), pendientes de sincronizar a Bitbucket (origin).

## Últimos commits de esta sesión (en orden)
1. `[FIX] Corregir websocket wss:// y flags de Chrome headless en Railway`
2. `[FIX] Quitar --remote-debugging-port fijo...`
3. `[TEMP] Activar log verbose de chromedriver para diagnosticar crash en Railway`
4. `[FIX] Pasar file object a log_output en vez de string`
5. `[FIX] Lanzar chromedriver como proceso independiente en vez de vía Selenium Service`
6. `[FIX] No usar /.dockerenv para detectar entorno Docker, causaba el crash real` ← **el fix probablemente definitivo**
7. `[FIX] Agregar logs y timeout explicito al arranque de chromedriver standalone`
8. `[FIX] Reenviar output del subprocess de pytest a los logs de Railway`
9. `[TEMP] Mostrar salida en vivo del test en la interfaz para diagnostico`
10. `[FIX] Quitar import time duplicado que rompia el chromedriver standalone` ← último commit, sin validar aún
