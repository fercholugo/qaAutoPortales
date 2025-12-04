# 🚀 QA Auto Portales - Framework de Automatización

## 📋 Descripción del Proyecto

**QA Auto Portales** es un framework de automatización de pruebas para portales cautivos, desarrollado en Python con arquitectura modular basada en el patrón Screenplay.

## 🛠️ Stack Tecnológico

- **Python 3.12**
- **Selenium WebDriver**
- **pytest + pytest-bdd** (BDD)
- **Docker** (deployment)

## 🚀 Instalación y Ejecución

### 📦 Con Docker (Recomendado)

#### Prerequisitos
- Docker y Docker Compose instalados

#### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <repo-url>
   cd qa-auto-portales
   ```

2. **Construir la imagen**
   ```bash
   docker-compose build
   ```

3. **Ejecutar las pruebas**
   ```bash
   docker-compose up
   ```
   - Los reportes y videos se guardan automáticamente en `./reporte_html/` (máquina local).

4. **Cambiar escenario a ejecutar**
   
   Edita la última línea del archivo `docker-compose.yml`:
   ```yaml
   command: ./run_tests.sh portal_normal varios
   ```
   Opciones:
   - `portal_normal unico` - Escenario único del portal normal
   - `portal_normal varios` - Múltiples ejemplos del portal normal
   - `portal_api unico` - Escenario único del portal API
   - `portal_api varios` - Múltiples ejemplos del portal API

5. **Ver el reporte**
   ```bash
   open reporte_html/reporte.html
   ```
   Los videos están en `./reporte_html/videos_ejecuciones/`.

---

### 💻 Sin Docker (Local)

#### Prerequisitos
- Python 3.12+
- Google Chrome instalado

#### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <repo-url>
   cd qa-auto-portales
   ```

2. **Crear entorno virtual e instalar dependencias**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Ejecutar las pruebas**
   ```bash
   RECORD_VIDEO=1 VIDEO_INTERVAL=0.3 ./run_tests.sh portal_normal unico
   ```
   Parámetros:
   - `portal_normal` o `portal_api` - Tipo de portal
   - `unico` o `varios` - Tipo de escenario

4. **Ver el reporte**
   - Se abre automáticamente en el navegador al finalizar.
   - O manualmente: `open reporte_html/reporte.html`

---

## 🧹 Limpieza

```bash
# Detener y eliminar contenedores Docker
docker-compose down

# Limpiar reportes locales
rm -rf reporte_html/
```

---

## 📁 Estructura del Proyecto

```
src/
├── abilities/       # Capacidades (navegación web)
├── actions/         # Acciones atómicas reutilizables
├── actors/          # Actores del sistema
├── tasks/           # Tareas de alto nivel
├── utils/           # Utilidades y helpers
└── questions/       # Validaciones

tests/               # Tests BDD con pytest
features/            # Archivos .feature (Gherkin)
reporte_html/        # Reportes y videos generados
```

---

**Desarrollado con Python + Selenium + Docker**