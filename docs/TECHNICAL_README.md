# 📘 Documentación Técnica - QA Automation Portales Cautivos

## 📋 Descripción general

Este proyecto automatiza la validación de flujos de portales cautivos para Datawifi usando
una arquitectura basada en el **patrón Screenplay** combinado con **BDD (Behavior Driven Development)**.

---

## 🛠️ Stack tecnológico

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| Python | 3.12+ | Lenguaje principal |
| Pytest | 8.3.4 | Ejecutor de pruebas |
| pytest-bdd | 8.1.0 | Integración BDD (Gherkin) |
| Selenium | latest | Automatización del navegador |
| ChromeDriver | latest | Driver para Chrome |
| pytest-html | 4.1.1 | Reportes HTML |
| allure-pytest | 2.15.0 | Reportes Allure interactivos |
| OpenCV (cv2) | latest | Grabación de video de ejecuciones |
| Guerrilla Mail API | - | Generación de correos temporales para validación por email |

---

## 📁 Estructura del proyecto

```
qa-auto-portales/
├── docs/
│   └── TECHNICAL_README.md            ← Este archivo
├── features/                          ← Archivos feature BDD (Gherkin)
│   └── portal_cautivo_normal_flujo_principal.feature
├── src/
│   ├── abilities/                     ← Capacidades del actor (navegación web)
│   │   └── browse_the_web.py
│   ├── actors/                        ← Actores Screenplay
│   │   └── actor.py
│   ├── tasks/                         ← Tareas de alto nivel
│   │   └── task_fill_portal_form.py   ← Lógica principal de interacción con formularios
│   ├── questions/                     ← Validaciones del flujo
│   │   └── is_on_expected_url.py
│   └── utils/                         ← Utilidades y helpers
│       ├── utils_guerrilla_mail.py    ← Manejo de correos temporales (Guerrilla Mail)
│       ├── utils_detect_form_elements.py ← Detección dinámica de elementos del formulario
│       ├── util_random_generator_data.py ← Generación de datos aleatorios (MAC, etc.)
│       └── utils_video_recorder.py   ← Grabación de video con OpenCV
├── tests/                             ← Steps de prueba (pytest-bdd)
│   └── test_steps_portal_cautivo_normal_flujo_principal.py
├── reporte_html/                      ← Reportes y videos generados (se crea al ejecutar)
│   ├── videos_ejecuciones/
│   └── reporte.html
├── run_tests.sh                       ← Script principal de ejecución
├── pyproject.toml                     ← Configuración de Pytest
├── requirements.txt                   ← Dependencias Python
└── README.md                          ← Guía de instalación y ejecución
```

---

## 🎭 Arquitectura: Patrón Screenplay

El proyecto sigue el **Patrón Screenplay**, que organiza la automatización en capas:

- **Actor:** Representa al usuario que interactúa con el portal cautivo.
- **Abilities:** Capacidades del actor (por ejemplo, navegar en la web con Selenium).
- **Tasks:** Acciones de alto nivel que el actor realiza (llenar formulario, hacer clic en botones, etc.).
- **Questions:** Validaciones que el actor realiza al final del flujo (¿está en la URL esperada?).

---

## ⚙️ Funcionalidades principales

### 🔀 Generación automática de MAC
Cada ejecución genera una dirección MAC aleatoria para simular un nuevo dispositivo conectándose al portal cautivo. Esto garantiza que cada prueba sea independiente y no reutilice sesiones previas.

### 🖱️ Detección de pre-portal
El sistema detecta automáticamente el tipo de portal cautivo leyendo el campo oculto `input#nombre_portal` e interactúa con la pantalla de pre-portal según corresponda:

| Portal | Bloque seleccionado |
|--------|-------------------|
| Bancolombia | "Soy Cliente" |
| Banco Agrario | "Correo" |

### 📋 Interacción dinámica con formularios
La task `task_fill_portal_form.py` detecta e interactúa dinámicamente con todos los elementos del formulario:

- Inputs de texto
- Inputs de email (con integración automática de Guerrilla Mail cuando se requiere)
- Checkboxes
- Select dropdowns
- Textareas
- Botones (Continuar, Validar)
- Imágenes clicables (opciones de navegación)

### 📧 Correo temporal (Guerrilla Mail)
Para portales que requieren validación por correo (ej. Banco Agrario), el flujo es:
1. Se detecta que el portal es de tipo Banco Agrario.
2. Se genera automáticamente un correo temporal vía API de Guerrilla Mail.
3. El correo se ingresa en el campo de email del formulario.
4. Se hace clic en el botón "Validar".
5. El sistema espera la llegada del correo con el PIN.
6. El PIN es extraído automáticamente y diligenciado en el campo correspondiente.

### 🎥 Grabación de video
Cada ejecución de prueba es grabada usando **OpenCV**. Los videos se guardan en `reporte_html/videos_ejecuciones/` con nombre que incluye el portal y la fecha/hora de ejecución.

---

## ▶️ Ejecución de pruebas

### Portal único:
```bash
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal unico
```

### Múltiples portales:
```bash
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal varios
```

### Parámetros de ejecución:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `RECORD_VIDEO` | `1` | Activa la grabación de video |
| `VIDEO_INTERVAL` | `0.3` | Intervalo entre frames del video (segundos) |

---

## 🔗 Configuración de URLs de portales

Las URLs de los portales se configuran en:
```
features/portal_cautivo_normal_flujo_principal.feature
```

Cada URL sigue este formato:
```
https://app.datawifi.co/easyfi/web/app.php/portal?called=VALOR_CALLED&mac=
```

> ⚠️ El parámetro `mac=` debe dejarse **siempre vacío** — se genera automáticamente en tiempo de ejecución.

---

## 📊 Reportes

| Reporte | Ubicación | Descripción |
|---------|-----------|-------------|
| HTML | `reporte_html/reporte.html` | Reporte completo de ejecución con resultados y logs |
| Videos | `reporte_html/videos_ejecuciones/` | Grabaciones de cada sesión de prueba |
| Allure | Generado con CLI de allure | Reporte interactivo avanzado con métricas |
