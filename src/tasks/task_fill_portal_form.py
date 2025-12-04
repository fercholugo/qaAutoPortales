from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By
from src.utils.util_random_generator_data import RandomGeneratorData
from src.utils.utils_detect_form_elements import detect_form_elements
import re
import time
import random
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class TaskFillPortalForm:
    # Variables de clase para trazabilidad
    generated_mac = None
    task_logs = []

    def __init__(self, form_data):
        self.form_data = form_data  # Diccionario con los datos a llenar
        TaskFillPortalForm.task_logs = []  # Reiniciar logs por ejecución

    @classmethod
    def log_and_print(cls, message):
        print(message)
        cls.task_logs.append(message)

    @classmethod
    def get_execution_info(cls):
        return {
            'mac': cls.generated_mac,
            'logs': cls.task_logs.copy()
        }

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        url = self.form_data.get("url")
        # Generar MAC aleatoria y reemplazar en la URL
        mac = RandomGeneratorData.generate_random_mac()
        url = re.sub(r"mac=([A-Za-z0-9]*)", f"mac={mac}", url)
        TaskFillPortalForm.generated_mac = mac
        TaskFillPortalForm.log_and_print(f"[Task] MAC generada: {mac}")
        TaskFillPortalForm.log_and_print(f"[Task] URL navegada: {url}")
        driver.get(url)
        driver.implicitly_wait(3)
        # Detección modular y reutilizable
        detect_form_elements(driver)
        panels = driver.find_elements(By.CLASS_NAME, 'panel_portal')
        TaskFillPortalForm.log_and_print(f"[Screenplay] Paneles encontrados: {len(panels)}")
        TaskFillPortalForm.log_and_print("\n[Screenplay] === DETECCIÓN E INTERACCIÓN DE ELEMENTOS DEL FORMULARIO ===")
        for panel_idx, panel in enumerate(panels):
            TaskFillPortalForm.log_and_print(f"\nPanel {panel_idx+1} (id={panel.get_attribute('id')}):")
            # Inputs
            inputs = panel.find_elements(By.XPATH, ".//input[not(@type='hidden')]")
            for input_element in inputs:
                input_type = input_element.get_attribute('type')
                placeholder = input_element.get_attribute('placeholder')
                value = None
                if input_type == 'text':
                    if placeholder and 'celular' in placeholder.lower():
                        value = RandomGeneratorData.generate_random_phone()
                    else:
                        value = "Test Nombre"
                elif input_type == 'email':
                    value = "test@correo.com"
                elif input_type == 'tel':
                    value = RandomGeneratorData.generate_random_phone()
                elif input_type == 'checkbox':
                    if not input_element.is_selected():
                        try:
                            input_element.click()
                            value = "checked"
                        except Exception:
                            driver.execute_script("arguments[0].click();", input_element)
                            value = "checked (JS)"
                    else:
                        value = "already checked"
                elif input_type == 'radio':
                    if not input_element.is_selected():
                        input_element.click()
                        value = "selected"
                elif input_type == 'password':
                    value = "TestPass123"
                else:
                    value = "Test Data"
                if value is not None and input_type not in ['checkbox', 'radio']:
                    try:
                        input_element.clear()
                        input_element.send_keys(value)
                    except Exception:
                        driver.execute_script("arguments[0].value = arguments[1];", input_element, value)
                TaskFillPortalForm.log_and_print(f"  INPUT: type={input_type}, value={value}")
            # Selects
            select_elements = panel.find_elements(By.TAG_NAME, 'select')
            for select_element in select_elements:
                valid_options = []
                selected_option = None
                try:
                    select = Select(select_element)
                    valid_options = [option for option in select.options if option.get_attribute('value') != 'no_respuesta']
                    if valid_options:
                        selected_option = random.choice(valid_options)
                        select.select_by_value(selected_option.get_attribute('value'))
                        TaskFillPortalForm.log_and_print(f"  SELECT: value={selected_option.get_attribute('value')}, text={selected_option.text}")
                    else:
                        TaskFillPortalForm.log_and_print("  SELECT: No hay opciones válidas para seleccionar.")
                except Exception:
                    # Interacción forzada con JS si la normal falla
                    if valid_options and selected_option:
                        driver.execute_script("arguments[0].value = arguments[1];", select_element, selected_option.get_attribute('value'))
                        TaskFillPortalForm.log_and_print(f"  SELECT: valor seleccionado (forzado JS)='{selected_option.get_attribute('value')}'")
            # Textareas
            text_areas = panel.find_elements(By.TAG_NAME, 'textarea')
            for text_area in text_areas:
                value = "Test texto area"
                try:
                    text_area.clear()
                    text_area.send_keys(value)
                except Exception:
                    driver.execute_script("arguments[0].value = arguments[1];", text_area, value)
                TaskFillPortalForm.log_and_print(f"  TEXTAREA: value={value}")
            # Botones continuar
            buttons = panel.find_elements(By.CLASS_NAME, 'continuar')
            for button in buttons:
                try:
                    if button.is_enabled():
                        button.click()
                        TaskFillPortalForm.log_and_print(f"  BOTÓN CONTINUAR: '{button.text}' clickeado")
                    else:
                        TaskFillPortalForm.log_and_print(f"  BOTÓN CONTINUAR: '{button.text}' no habilitado, esperando que se habilite...")
                        try:
                            WebDriverWait(driver, 12).until(lambda d: button.is_enabled())
                            button.click()
                            TaskFillPortalForm.log_and_print(f"  BOTÓN CONTINUAR: '{button.text}' habilitado tras espera y clickeado")
                        except TimeoutException:
                            TaskFillPortalForm.log_and_print(f"  BOTÓN CONTINUAR: '{button.text}' no se habilitó tras 12s, no se pudo clicar")
                except Exception:
                    driver.execute_script("arguments[0].click();", button)
                    TaskFillPortalForm.log_and_print(f"  BOTÓN CONTINUAR: '{button.text}' clickeado (JS)")
        TaskFillPortalForm.log_and_print("\n[Screenplay] === FIN DILIGENCIAMIENTO DE ELEMENTOS ===\n")
        time.sleep(2)
