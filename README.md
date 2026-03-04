# 🚀 QA Auto Portales - Framework de Automatización

> 📖 Para documentación técnica detallada, consulta [`docs/TECHNICAL_README.md`](docs/TECHNICAL_README.md)

## 📋 Descripción

Proyecto de automatización de pruebas para portales cautivos Datawifi, desarrollado en Python con Selenium, Pytest y BDD.

---

## ✅ Requisitos del sistema

- Python 3.12+
- Google Chrome (última versión)
- ChromeDriver (compatible con tu versión de Chrome)
- macOS o Linux
- Bash shell

---

## �� Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd qa-auto-portales
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Dar permisos de ejecución al script:**
   ```bash
   chmod +x run_tests.sh
   ```

---

## ⚙️ Configuración antes de ejecutar

Antes de ejecutar las pruebas, actualiza las URLs de los portales en el archivo feature:

```
features/portal_cautivo_normal_flujo_principal.feature
```

### Portal único:
Actualiza la URL en la sección `Scenario`:
```gherkin
Scenario: Flujo principal datos correctos portal cautivo normal (unico)
  Given que el usuario "Fernando" accede al portal cautivo en "chrome" con la url "https://app.datawifi.co/easyfi/web/app.php/portal?called=TU_CALLED&mac="
```

### Múltiples portales:
Actualiza las URLs en la tabla `Examples`:
```gherkin
Examples:
  | nombre_actor | navegador | url                                                                          |
  | Fernando     | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=TU_CALLED_1&mac=   |
  | Fernando     | chrome    | https://app.datawifi.co/easyfi/web/app.php/portal?called=TU_CALLED_2&mac=   |
```

> ⚠️ **Importante:** El parámetro `mac=` debe dejarse siempre vacío. El sistema lo genera automáticamente en cada ejecución.

---

## ▶️ Ejecución de pruebas

### Portal único (recomendado para validación rápida):
```bash
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal unico
```

### Múltiples portales:
```bash
RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal varios
```

---

## 📊 Reportes

Después de la ejecución, los reportes se generan automáticamente en:

```
reporte_html/
├── videos_ejecuciones/    ← Videos grabados de cada prueba
└── reporte.html           ← Reporte HTML completo
```

Abrir el reporte manualmente:
```bash
open reporte_html/reporte.html
```

---

## 🐳 Ejecución con Docker (opcional)

### Prerequisitos
- Docker y Docker Compose instalados

### Pasos

1. **Construir la imagen:**
   ```bash
   docker-compose build
   ```

2. **Ejecutar las pruebas:**
   ```bash
   docker-compose up
   ```

3. **Cambiar el escenario a ejecutar:**

   Edita la última línea del archivo `docker-compose.yml`:
   ```yaml
   command: ./run_tests.sh portal_normal varios
   ```

4. **Detener y limpiar contenedores:**
   ```bash
   docker-compose down
   ```

---

**Desarrollado con Python + Selenium + pytest-bdd**
