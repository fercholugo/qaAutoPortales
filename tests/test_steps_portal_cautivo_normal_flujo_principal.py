from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import time
import os
from datetime import datetime

from src.actors.actor import Actor
from src.abilities.browse_the_web import BrowseTheWeb
from src.tasks.task_fill_portal_form import TaskFillPortalForm
from src.questions.is_on_google import IsOnGoogle
from src.video.viewport_recorder import ViewportRecorder
from src.questions.is_on_expected_url import IsOnExpectedUrl


#para docker
from os.path import abspath, join, dirname


@pytest.fixture
def contexto():
    """Diccionario compartido entre los steps."""
    return {}


@given(parsers.parse('que el usuario "{nombre_actor}" accede al portal cautivo en "{navegador}" con la url "{url}"'))
def step_open_portal(contexto, nombre_actor, navegador, url, request):
    """
    Inicializa el actor y, si corresponde, arranca la grabación de video.
    """
    url = os.getenv("PORTAL_URL", url)  # override desde web UI si está definida
    form_data = {"url": url}
    contexto['actor'] = Actor(nombre_actor).can(BrowseTheWeb(navegador))
    contexto['form_data'] = form_data

    # Activación opcional de video por variable de entorno.
    if os.getenv("RECORD_VIDEO") == "1":
        alias = os.getenv("FEATURE_ALIAS", "portal_normal")
        keyword = os.getenv("SCENARIO_KEYWORD", "run")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Si VIDEO_DIR está definido (llamada desde web UI), usa ese directorio con nombre fijo.
        # Si no (CLI), usa el directorio histórico con nombre que incluye timestamp.
        videos_dir = os.getenv("VIDEO_DIR", "reporte_html/videos_ejecuciones")
        os.makedirs(videos_dir, exist_ok=True)
        nombre = "evidencia.mp4" if os.getenv("VIDEO_DIR") else f"{alias}_{keyword}_{ts}.mp4"
        video_path = os.path.join(videos_dir, nombre)

        driver = contexto['actor'].ability_to(BrowseTheWeb).driver
        intervalo = float(os.getenv("VIDEO_INTERVAL", "0.5"))  # Ajustable
        recorder = ViewportRecorder(driver, video_path, interval=intervalo)
        recorder.start()
        contexto['recorder'] = recorder
        contexto['video_path'] = video_path
        # Asocia el video a este test para que pytest-html lo muestre en "Links"
        request.node.video_path = video_path


@when('ingresa todos los datos obligatorios y validos en el formulario')
def step_fill_form(contexto):
    """
    Ejecuta la tarea de llenado del formulario en el portal.
    """
    task = TaskFillPortalForm(contexto['form_data'])
    task.perform_as(contexto['actor'])
    time.sleep(2)  # Pausa breve para estabilizar después del llenado.


@then('el flujo es finalizado y validado correctamente')
def step_form_sent(contexto):
    """
    Verifica la página final y detiene la grabación si estaba activa.
    """
    try:
        time.sleep(5)  # Espera final para redirección.
        assert IsOnExpectedUrl.answered_by(contexto['actor']), "El flujo no terminó en una URL esperada"
    finally:
        recorder = contexto.get('recorder')
        if recorder:
            recorder.stop()
        contexto['actor'].ability_to(BrowseTheWeb).quit()


# Asociación de escenarios del feature.
#scenarios('features/portal_cautivo_normal_flujo_principal.feature') #funciona en local

# prueba en docker
FEATURE_PATH = abspath(join(dirname(__file__), '..', 'features', 'portal_cautivo_normal_flujo_principal.feature'))
scenarios(FEATURE_PATH)