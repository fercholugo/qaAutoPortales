---
name: actualizar-portal
description: Diagnostica por qué falla un portal cautivo en qa-auto-portales (o agrega uno nuevo) usando la evidencia real de la ejecución (pagina.html, video, reporte), y propone el ajuste mínimo a la lógica determinista de detección/interacción. Activar SIEMPRE que el usuario escriba las frases "sk actualizar portal X", "sk agregar portal X", o "sk portal falla X" (X = nombre del portal) — estas son las frases de activación preferidas del usuario, tratarlas como comando directo sin pedir aclaración. También activar si dice "el portal X esta fallando", "agregar portal nuevo", "actualicemos el flujo de X", "por que falla [portal]", o pida ayuda de mantenimiento sobre un portal cautivo específico.
---

# Actualizar / diagnosticar flujo de un portal cautivo

## Qué es esto y qué NO es

Este skill es una **herramienta de desarrollo**, no participa en la ejecución real de los tests. La ejecución del proyecto debe seguir siendo 100% determinista: nunca agregues llamadas a un modelo de IA dentro de `src/`. El trabajo de este skill es ayudar al desarrollador (vos) a escribir/corregir código determinista más rápido, usando evidencia real capturada durante una ejecución.

## Contexto del proyecto

- `server/portales.json` — lista de portales: `id`, `nombre`, `url`, `feature_alias`. Si un portal no está aquí, no aparece seleccionable en la interfaz web.
- `src/tasks/task_fill_portal_form.py` — **archivo crítico**, requiere confirmación explícita del usuario antes de editar (regla del proyecto en CLAUDE.md). Contiene:
  - Lectura de `#nombre_portal` (input hidden) para identificar qué portal cargó.
  - Un `if/elif` que decide qué `div.bloque` pre-portal clickear según el valor de `nombre_portal` (algunos portales tienen una pantalla previa tipo "Soy Cliente" / "Aun No Soy Cliente" antes de llegar al formulario real).
  - Lógica **genérica** de detección/llenado de `panel_portal` (inputs, selects, textareas, checkboxes, botón continuar) — esta parte ya es robusta y no debería necesitar cambios por portal; si el bloque pre-portal correcto se selecciona, esta lógica se encarga sola del resto.
- `src/utils/utils_detect_form_elements.py` — cuando no encuentra ningún elemento con id que empiece por `panel`, guarda el HTML completo de la página en `{VIDEO_DIR}/pagina.html` (mismo directorio que el video y el reporte). Esta es la evidencia clave para este skill.
- Cada ejecución (local o vía la interfaz web) genera en `reporte_html/runs/{run_id}/{portal_id}/`: `reporte.html`, `evidencia.mp4`, y (si aplica) `pagina.html`.
- En producción (Railway), esa carpeta es accesible vía `https://<dominio>/reportes/runs/{run_id}/{portal_id}/pagina.html`.

## Proceso paso a paso

### Paso 0 — ¿Existe el portal en `portales.json`?

Pregunta o infiere el nombre/id del portal. Lee `server/portales.json`.

- **Si NO existe** (portal totalmente nuevo): ayuda a construir la entrada (`id`, `nombre`, `url`, `feature_alias` — casi siempre `"portal_normal"`). Muestra el diff exacto y espera confirmación explícita antes de escribir (no es un archivo "crítico" listado en CLAUDE.md, pero igual sigue la regla general: nunca editar sin autorización explícita del usuario).
- **Si ya existe**: continúa al paso 1.

### Paso 1 — Generar o localizar evidencia fresca

Necesitas una ejecución reciente de ese portal con evidencia (`pagina.html` y/o el reporte).

- Si el usuario ya te compartió el log de una ejecución fallida (pegado en el chat) con un `run_id`, úsalo directamente — no hace falta re-ejecutar.
- Si no hay ejecución reciente: pídele al usuario que corra el test para ese portal (desde la interfaz web, o localmente con `./run_tests.sh` si prefiere iterar más rápido sin esperar redeploys — ver `docs/TECHNICAL_README.md` / `CLAUDE.md` para el comando exacto). Para un portal nuevo, es normal y esperado que la **primera ejecución falle** — ese primer fallo es en sí mismo el paso de diagnóstico, no lo trates como un problema aparte.

### Paso 2 — Ubicar la carpeta de evidencia

`reporte_html/runs/{run_id}/{portal_id}/` (local) o `/reportes/runs/{run_id}/{portal_id}/` (Railway, vía `curl` o el navegador).

### Paso 3 — Leer `pagina.html` crudo

Si corriste local, usa Read directamente sobre el archivo. Si es de Railway, usa `curl -s <url>/pagina.html -o /tmp/<algo>.html` y luego Read/grep sobre el archivo local — **no uses WebFetch para esto**, convierte el HTML a markdown y pierde atributos/estructura exactos que necesitas.

### Paso 4 — Verificar el valor real de `#nombre_portal`

```
grep -o 'id="nombre_portal"[^>]*' <archivo>
```

**No asumas** que va a contener el nombre del banco/cliente — puede identificarse por el proveedor de red u otro criterio interno (ej. Santander México se identifica como `"work Cafe preportal@Telmex.mx"`, sin la palabra "santander").

### Paso 5 — Verificar los `div.bloque` (o el contenedor pre-portal que aplique)

Busca todas las ocurrencias de la clase (puede no ser la primera clase en el atributo, ej. `class="text-center col-xs-12 ... bloque"` — no busques `class="bloque` literal, busca la palabra `bloque` en cualquier posición). Anota:
- Cuántos bloques hay y en qué orden aparecen en el DOM.
- Qué atributo identifica su acción (ej. `data-nombrebloque`, `.url_redireccion`).
- **No confíes en el texto visible** ("Soy Cliente" puede ser una imagen/CSS, no texto plano en el DOM).

### Paso 5.5 — Descartar que sea un error del backend del portal (fuera de alcance)

Antes de comparar contra el código, revisa si `pagina.html` es en realidad una **pantalla de error genérica del portal**, no el formulario esperado. Señales típicas:
- `<title>Error</title>` (o similar) en vez del título normal del portal.
- Sin `#nombre_portal`, sin `div.bloque`, sin ningún `panel_portal` — la página está vacía de esos elementos porque nunca llegó a cargar el flujo real.
- Texto tipo "problema de configuración", "el dispositivo no está asignado a una zona", o mensajes dirigidos al administrador de la red (no al usuario final).

Si ves esto: **no es un bug de detección ni de código**. Es un problema de aprovisionamiento del identificador `called=` (o del MAC) en el sistema del portal/red — algo que corregir con el administrador del portal, no con un ajuste a `task_fill_portal_form.py`. Repórtalo así al usuario y detente aquí; no propongas un fix de código para este caso.

### Paso 6 — Comparar contra el código actual

Lee el `if/elif` en `src/tasks/task_fill_portal_form.py` (busca `nombre_portal.lower()`) y compara contra lo que encontraste en los pasos 4-5. El mismatch suele ser uno de estos tres:
1. Falta una rama completa para este portal.
2. El string de comparación no coincide con el valor real (como pasó con Santander/Telmex).
3. El índice de bloque elegido (`bloques[0]`, `bloques[1]`, etc.) no corresponde al bloque correcto.

### Paso 7 — Proponer el fix mínimo

Muestra el diff exacto (solo la rama nueva o corregida, sin tocar nada más) y **espera confirmación explícita** del usuario antes de aplicar — este archivo está en la lista de archivos críticos de CLAUDE.md.

### Paso 8 — Aplicar, desplegar y re-probar

Tras la confirmación: aplica el cambio, commitea, pushea (si aplica el flujo de Railway), y pide al usuario que vuelva a correr el test.

- **Si pasa**: confirma que la lógica genérica de `panel_portal` se encargó sola del resto — no se necesitan más cambios para este portal.
- **Si sigue fallando pero ya pasó de "0 paneles encontrados"** (o sea, ya entra al panel pero falla más adelante, en el llenado de un campo específico o un botón particular): esto es un problema distinto, de personalización dentro del panel, no de selección de bloque pre-portal. Vuelve a los pasos 3-5 pero enfocado en el HTML/log de esa etapa posterior, y trátalo como un caso nuevo de diagnóstico — no asumas que aplica el mismo tipo de fix.

## Lecciones aprendidas (gotchas ya encontrados)

Antes de diagnosticar un caso nuevo, revisa esta lista — puede que ya hayamos visto algo parecido. Agrega una entrada nueva cada vez que se descubra un patrón/tropiezo distinto (síntoma → causa real → qué se hizo), en una sola línea, sin explicaciones largas.

- **Santander México / Telmex**: el portal se identifica en `#nombre_portal` como `"work Cafe preportal@Telmex.mx"`, no contiene "santander". No asumir que el nombre del banco aparece ahí.
- **Centros Digitales**: página de error del backend (`<title>Error</title>`, "dispositivo no asignado a una zona") — NO es bug de código, es aprovisionamiento del `called=` en el sistema del portal.
- **Sitwifi**: video obligatorio antes de habilitar "Navegar ahora" — es un iframe de YouTube (`class="youtube_video"`), no una etiqueta `<video>` nativa. El botón nunca queda `disabled`, pero el sitio bloquea la navegación por JS hasta que un flag oculto (`class="banderin_video"`, mismo id numérico que el iframe) pase a `"1"`. Se reproduce vía `postMessage` (`playVideo`) y se espera ese flag — no confiar en un botón "Omitir video" genérico, no siempre existe.

## Recordatorios de seguridad (heredados de CLAUDE.md)

- Nunca edites `task_fill_portal_form.py`, `portales.json`, u otro archivo sin mostrar el diff exacto y esperar una confirmación explícita ("aplícalo", "procede", "impleméntalo", etc.).
- Un archivo a la vez. No hagas ediciones adicionales "aprovechando" que ya estás en el archivo.
- Si el usuario está en modo que no permite editar, dilo explícitamente — nunca digas que aplicaste un cambio si no se pudo ejecutar.