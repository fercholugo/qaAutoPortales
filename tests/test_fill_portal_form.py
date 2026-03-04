import time
from src.actors.actor import Actor
from src.abilities.browse_the_web import BrowseTheWeb
from src.tasks.task_fill_portal_form import TaskFillPortalForm
from src.utils.util_random_generator_data import RandomGeneratorData

# Datos del portal cautivo
PORTAL_URL = "https://qa.datawifi.co/easyfi/web/app.php/portal?called=f89e2875a8aa&mac="

def test_fill_portal_form():
    mac = RandomGeneratorData.generate_random_mac()
    url = PORTAL_URL + mac
    form_data = {
        "url": url,
        # Puedes agregar aquí los nombres de los campos y valores si los conoces
        # "nombre": "Juan",
        # "email": "juan@ejemplo.com",
    }
    actor = Actor("Tester").can(BrowseTheWeb("chrome"))
    task = TaskFillPortalForm(form_data)
    task.perform_as(actor)
    # Esperar unos segundos para ver el resultado manualmente
    time.sleep(5)
    # Cerrar el navegador
    #actor.ability_to(BrowseTheWeb).quit()

if __name__ == "__main__":
    test_fill_portal_form()
