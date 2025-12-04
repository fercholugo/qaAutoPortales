import pytest
import os
import sys

# Redefine el directorio raíz del proyecto para pytest-bdd (funciona en local y Docker)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.feature_reader import get_scenario_by_keyword, get_feature_title, get_task_execution_logs

# Silenciar ruido de librerías que contamina el reporte HTML relacionados con imageio y urllib3
import logging
import warnings

logging.getLogger("imageio_ffmpeg").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*IMAGEIO FFMPEG WRITER WARNING.*")

FEATURE_MAP = {
    "portal_normal": "features/portal_cautivo_normal_flujo_principal.feature",
    "portal_api": "features/portal_cautivo_api_flujo_principal.feature"
}

def get_feature_file_from_env():
    # Lee el alias desde variable de entorno (set por run_tests.sh antes de pytest)
    alias = os.environ.get("FEATURE_ALIAS", "portal_normal")
    return FEATURE_MAP.get(alias, "features/portal_cautivo_normal_flujo_principal.feature")

def pytest_html_results_table_html(report, data):
    if hasattr(report, 'nodeid'):
        # Extraer la palabra clave del test ejecutado (ej: "unico", "varios")
        test_name = report.nodeid.split("::")[-1] if "::" in report.nodeid else report.nodeid
        # Buscar palabra clave relevante
        keywords = ["unico", "varios"]
        scenario_keyword = None
        for k in keywords:
            if k in test_name:
                scenario_keyword = k
                break
        feature_file = get_feature_file_from_env()
        feature_title = get_feature_title(feature_file)
        scenario_content = get_scenario_by_keyword(feature_file, scenario_keyword)

        scenario_html = f"""
        <div style="margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; background-color: #f9f9f9;">
            <h4 style="color: #007cba; margin: 0 0 10px 0;">{feature_title}</h4>
            <pre style="background-color: #fff; padding: 10px; border: 1px solid #ddd; white-space: pre-wrap;">{scenario_content}</pre>
        </div>
        """
        data.append(scenario_html)
        # Mostrar los logs de la Task
        logs = get_task_execution_logs()
        if logs:
            logs_html = """
            <div style=\"margin: 10px 0; padding: 10px; border-left: 4px solid #28a745; background-color: #f8f9fa;\">
                <h4 style=\"color: #28a745; margin: 0 0 10px 0;\">Logs de Ejecución:</h4>
                <pre style=\"background-color: #fff; padding: 10px; border: 1px solid #ddd; white-space: pre-wrap; font-family: monospace; font-size: 12px;\">"""
            for log in logs:
                logs_html += f"{log}\n"
            logs_html += "</pre></div>"
            data.append(logs_html)

def pytest_html_results_table_row(report, cells):
    # Elimina celdas de log ruidosas en el reporte
    patterns = (
        "No log output captured.",
        "IMAGEIO FFMPEG WRITER WARNING",
        "imageio_ffmpeg",
        "Connection pool is full",
        "urllib3.connectionpool",
    )
    for i, cell in enumerate(cells):
        text = str(cell)
        if any(p in text for p in patterns):
            cells[i] = ""
try:
    from pytest_html import extras as html_extras
except Exception:
    html_extras = None

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    video_path = getattr(item, "video_path", None)
    if not video_path or not os.path.exists(video_path):
        return
    
    # Carpeta del reporte para crear ruta relativa
    html_path = getattr(item.config.option, "htmlpath", "reporte_html/reporte.html")
    html_dir = os.path.dirname(html_path)
    rel_path = os.path.relpath(video_path, start=html_dir)
    report.extra = getattr(report, "extra", [])

    # NUEVO: usar extras.url para que aparezca en la columna Links
    if html_extras:
        report.extra.append(html_extras.url(rel_path, "Ver Video"))    
    else:
        # Fallback: si no está pytest_html.extras, seguirá en el área de log
        report.extra.append(f'<a href="{rel_path}" target="_blank">Ver Video</a>')



def pytest_html_report_title(report):
    report.title = "Reporte de Pruebas Portal Cautivo"

def pytest_html_results_summary(prefix, summary, postfix):
    # Busca y mueve la sección Environment si existe
    for i, section in enumerate(summary):
        if "Platform" in str(section) and "Python" in str(section):
            env_section = summary.pop(i)
            postfix.append(env_section)
            break

    js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('td, .log').forEach(function(el) {
            if (el.textContent.includes('No log output captured.')) {
                el.style.display = 'none';
            }
        });
    });
    </script>
    """
    return [js]