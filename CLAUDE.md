# CLAUDE.md — QA Auto Portales

## AUTO-CARGA DE SESIÓN ANTERIOR

Al iniciar cada conversación, ejecuta inmediatamente este comando:

```bash
ls docs/session-checkpoints/*.md 2>/dev/null | sort -r | head -1
```

**Si el comando retorna una ruta de archivo:**
1. Lee ese archivo completo con la herramienta Read
2. Incorpora todo su contenido en tu contexto de sesión: objetivo, archivos relevantes, progreso, decisiones tomadas, problemas conocidos
3. Muestra al usuario **una sola línea** de confirmación con este formato:
   > 📋 Contexto cargado: {tarea del checkpoint} — {estado en curso en pocas palabras}. ¿En qué te ayudo?
4. Continúa normal. No pidas confirmación ni esperes respuesta especial del usuario.

**Si el comando no retorna nada** (directorio vacío o no existe): omite este paso silenciosamente y continúa.

---

## SUGERENCIA PROACTIVA DE CHECKPOINT

Durante la conversación, estima el uso de contexto en cada respuesta usando esta heurística:
- Sesión ligera (consultas, planificación): ~3,000 tokens/intercambio → ~60 msgs totales
- Sesión media (lectura de archivos, análisis): ~6,000 tokens/intercambio → ~33 msgs totales
- Sesión pesada (ediciones, tests con output): ~10,000 tokens/intercambio → ~20 msgs totales

Si estimas que quedan **menos de 20 mensajes** de contexto útil, agrega al final de tu respuesta:

> ⚠️ Estimo ~{N} mensajes restantes antes del límite de contexto. Considera ejecutar `/save-session {nombre-tarea}` para no perder el progreso.

---

## REGLAS DE TRABAJO

### Autorización explícita para modificar código

**NUNCA** editar o crear archivos de código sin que el usuario diga explícitamente:
"Aplica los cambios" / "Procede" / "Actualiza el archivo" / "Implementa" / "Hazlo"

**Proceso obligatorio para cualquier cambio:**
1. Leer el archivo actual
2. Analizar y mostrar el fragmento propuesto (solo el bloque a cambiar)
3. Indicar exactamente dónde va el cambio (línea/función)
4. **Detenerse y esperar confirmación explícita**
5. Solo tras confirmación: aplicar el cambio
6. Confirmar qué se cambió y qué NO se tocó

### Edición quirúrgica
- NUNCA reescribir archivos completos
- Usar `# ...existing code...` para representar código que no se modifica
- Aplicar solo el cambio solicitado, nada más adyacente

### Archivos críticos (confirmación explícita obligatoria)
- `src/tasks/task_fill_portal_form.py`
- `tests/test_steps_*.py`
- `src/questions/*.py`
- `features/*.feature`
- `conftest.py` · `pyproject.toml` · `docker-compose.yml` · `.env`

### Cambios graduales
- Un archivo a la vez
- Esperar confirmación antes del siguiente paso
- No hacer múltiples ediciones seguidas sin confirmación

### Comentarios y documentación
- Cada función nueva o modificada debe incluir un docstring con su propósito
- Comentarios concisos en español orientados a mantenimiento
- No eliminar comentarios existentes sin justificar y confirmar con el usuario

### Transparencia sobre limitaciones
- Si estoy en modo "ask" y no puedo editar archivos, decirlo inmediatamente
- NUNCA decir que "se aplicó" un cambio si no fue posible ejecutarlo

---

## REGLAS PARA ELEMENTOS INTERACTIVOS (flujos de automatización)

1. Todo elemento interactivo recurrente (inputs, selects, textareas, botones) debe recorrerse con `for` sobre la colección
2. Buscar siempre dentro del contexto del panel actual (`panel.find_elements(...)`)
3. Validar `is_enabled()`, no solo `is_displayed()` (soporte headless)
4. Si el clic normal falla, intentar con JS: `driver.execute_script("arguments[0].click();", elemento)`
5. Registrar cada acción en el log del flujo

---

## CONTEXTO TÉCNICO DEL PROYECTO

**Stack:** Python 3.12 · Selenium 4.28 · pytest-bdd 8.1 · ScreenPy 4.2 (Screenplay pattern) · Guerrilla Mail API · imageio (grabación de video)

**Ejecutar tests:**
```bash
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal unico
```

**Estructura:**
```
qa-auto-portales/
├── features/          ← Escenarios BDD (.feature)
├── src/
│   ├── tasks/         ← task_fill_portal_form.py (lógica principal)
│   ├── questions/     ← Validaciones post-flujo
│   ├── abilities/     ← Capacidades Selenium del actor
│   └── utils/         ← Guerrilla Mail, video, MAC generation, detección de elementos
├── tests/             ← Steps pytest-bdd
├── docs/
│   ├── TECHNICAL_README.md
│   └── session-checkpoints/   ← Checkpoints de sesión (/save-session)
├── .ai-instructions.md        ← Reglas de trabajo AI (referencia autoritativa)
└── run_tests.sh               ← Script principal de ejecución
```

**Detalles clave:**
- Cada test genera una MAC aleatoria por ejecución
- Portales que requieren PIN usan Guerrilla Mail API para correos temporales
- El flujo detecta automáticamente campos de formulario (inputs, selects, textareas, botones)
- Los tests graban video de la ejecución para depuración
