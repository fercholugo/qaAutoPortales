# Script para personalizar el reporte HTML generado por pytest-html
# Uso: python personalizar_reporte.py

import os
import re

REPORTE_PATH = os.path.join(os.path.dirname(__file__), "reporte.html")

JS_OCULTAR_LOG = '''<script>
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('td, .log').forEach(function(el) {
        if (el.textContent.includes('No log output captured.')) {
            el.style.display = 'none';
        }
    });
});
</script>'''

def eliminar_log_vacio(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # Elimina el texto del log vacío
    html = html.replace("No log output captured.", "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Texto 'No log output captured.' eliminado del reporte.")

def mover_environment_despues_de_resultados(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # Busca el bloque Environment
    env_pattern = r'(\s*<div id="environment-header">[\s\S]*?<table id="environment">[\s\S]*?</table>)'
    env_match = re.search(env_pattern, html)
    if env_match:
        env_block = env_match.group(1)
        html = html.replace(env_block, "")
        # Busca la tabla de resultados
        results_pattern = r'(<table id="results-table">[\s\S]*?</table>)'
        results_match = re.search(results_pattern, html)
        if results_match:
            results_block = results_match.group(1)
            html = html.replace(results_block, results_block + env_block)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print("Sección 'Environment' movida debajo de la tabla de resultados.")
        else:
            print("No se encontró la tabla de resultados.")
    else:
        print("No se encontró el bloque 'Environment'.")

def agregar_js_ocultar_log(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # Inserta el JS antes de </body>
    if JS_OCULTAR_LOG not in html:
        html = html.replace("</body>", JS_OCULTAR_LOG + "\n</body>")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("Personalización aplicada: log oculto.")
    else:
        print("El JS ya está presente en el reporte.")

if __name__ == "__main__":
    if os.path.exists(REPORTE_PATH):
        eliminar_log_vacio(REPORTE_PATH)
        mover_environment_despues_de_resultados(REPORTE_PATH)
        agregar_js_ocultar_log(REPORTE_PATH)
    else:
        print(f"No se encontró el archivo: {REPORTE_PATH}")
