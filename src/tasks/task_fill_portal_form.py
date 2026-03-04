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

# import para generar correo temporal Guerrilla Mail
from src.utils.utils_guerrilla_mail import generar_correo, leer_codigo


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
        
        # --- NUEVO: Click en "Continúa sin redes sociales" SI EXISTE (antes de buscar paneles) ---
        try:
            btn_continue_sin_redes = driver.find_element(By.XPATH, "//button[contains(., 'Continúa sin redes sociales')]")
            if btn_continue_sin_redes.is_enabled():
                try:
                    btn_continue_sin_redes.click()
                    TaskFillPortalForm.log_and_print("[Task] Botón 'Continúa sin redes sociales' clickeado normalmente.")
                    driver.implicitly_wait(3)  # Esperar a que cargue el formulario
                except Exception:
                    driver.execute_script("arguments[0].click();", btn_continue_sin_redes)
                    TaskFillPortalForm.log_and_print("[Task] Botón 'Continúa sin redes sociales' clickeado por JS.")
                    driver.implicitly_wait(3)
        except Exception:
            TaskFillPortalForm.log_and_print("[Task] Botón 'Continúa sin redes sociales' no encontrado, continuando con el flujo normal.")
        # --- FIN NUEVO ---

        # --- NUEVO: Click en BLOQUE IMAGEN según portal detectado por input#nombre_portal ---
        # Detectar el portal por input#nombre_portal (hidden con valor identificable)
        nombre_portal = ""
        try:
            nombre_portal = driver.find_element(By.ID, "nombre_portal").get_attribute("value") or ""
            TaskFillPortalForm.log_and_print(f"[Task] Portal detectado: {nombre_portal}")
        except Exception:
            TaskFillPortalForm.log_and_print("[Task] No se pudo leer el nombre del portal.")

        # Click en div.bloque según el portal detectado
        try:
            bloques = driver.find_elements(By.CSS_SELECTOR, 'div.bloque')
            if bloques:
                bloque_seleccionado = None
                if "bancolombia" in nombre_portal.lower():
                    bloque_seleccionado = bloques[0]  # "Soy cliente"
                    TaskFillPortalForm.log_and_print("[Task] Portal Bancolombia → seleccionando bloque 'Soy Cliente'.")
                elif "bancoagrario" in nombre_portal.lower() and len(bloques) > 1:
                    bloque_seleccionado = bloques[1]  # "Correo"
                    TaskFillPortalForm.log_and_print("[Task] Portal Banco Agrario → seleccionando bloque 'Correo'.")
                if bloque_seleccionado:
                    driver.execute_script("arguments[0].scrollIntoView();", bloque_seleccionado)
                    driver.execute_script("arguments[0].click();", bloque_seleccionado)
                    TaskFillPortalForm.log_and_print("[Task] Pre-portal: bloque clickeado por JS exitosamente.")
                    driver.implicitly_wait(3)
                else:
                    TaskFillPortalForm.log_and_print("[Task] No se identificó ningún portal conocido en los bloques.")
        except Exception as e:
            TaskFillPortalForm.log_and_print(f"[Task] Error en la detección de bloques pre-portal: {e}")
        # --- FIN Click en BLOQUE IMAGEN ---

        # --- Generar correo temporal Guerrilla Mail SOLO si es Necesario ejemplo: (Banco Agrario) ---
        guerrilla_email = None
        guerrilla_sid = None
        if "bancoagrario" in nombre_portal.lower():
            try:
                guerrilla_email, guerrilla_sid = generar_correo()
                TaskFillPortalForm.log_and_print(f"[Task] Correo temporal generado: {guerrilla_email}")
            except Exception as e:
                TaskFillPortalForm.log_and_print(f"[Task] Error generando correo temporal: {e}")
        # --- FIN Generar correo temporal ---

        # Buscar los paneles del formulario (clase 'panel_portal')
        panels = driver.find_elements(By.CLASS_NAME, 'panel_portal')

        #traer todo el html de los paneles a la consola para verificar su estructura:
        TaskFillPortalForm.log_and_print(f"[Screenplay] Paneles encontrados: {len(panels)}")
        TaskFillPortalForm.log_and_print("\n[Screenplay] === DETECCIÓN E INTERACCIÓN DE ELEMENTOS DEL FORMULARIO ===")
        for panel_idx, panel in enumerate(panels):
            TaskFillPortalForm.log_and_print(f"\nPanel {panel_idx+1} (id={panel.get_attribute('id')}):")

            # Inputs
            inputs = panel.find_elements(By.XPATH, ".//input[not(@type='hidden')]")
            for input_element in inputs:
                input_type = input_element.get_attribute('type')
                placeholder = input_element.get_attribute('placeholder')

                # Saltar input#pin (se llenará con código Guerrilla Mail)
                input_id_check = input_element.get_attribute('id') or ""
                if input_id_check == 'pin':
                    TaskFillPortalForm.log_and_print("  INPUT#pin:(se llenará con código Guerrilla Mail)")
                    continue

                value = None
                if input_type == 'text':
                    if placeholder and 'celular' in placeholder.lower():
                        value = RandomGeneratorData.generate_random_phone()
                    else:
                        value = "Test Nombre"
                elif input_type == 'email':
                     # Si el input es para validación por correo (id="correo_validar") usa Guerrilla Mail
                    input_id = input_element.get_attribute('id')
                    if input_id == 'correo_validar' and guerrilla_email:
                        value = guerrilla_email
                        TaskFillPortalForm.log_and_print(f"  INPUT email de validación: usando correo Guerrilla Mail →  {value}")
                    else:
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
                        value = selected_option.get_attribute('value')
                        if value is not None:
                            select.select_by_value(value)
                            TaskFillPortalForm.log_and_print(f"  SELECT: value={value}, text={selected_option.text}")
                        else:
                            TaskFillPortalForm.log_and_print(f"  SELECT: opción sin valor, no se puede seleccionar.")
                    else:
                        TaskFillPortalForm.log_and_print("  SELECT: No hay opciones válidas para seleccionar.")
                except Exception:
                    # Interacción forzada con JS si la normal falla
                    if valid_options and selected_option:
                        driver.execute_script("arguments[0].value = arguments[1];", select_element, selected_option.get_attribute('value'))
                        TaskFillPortalForm.log_and_print(f"  SELECT: valor seleccionado (forzado JS)='{selected_option.get_attribute('value')}'")

                    # Forzar SELECT a 'EMAIL' si el portal requiere validación por correo
                    if guerrilla_email:
                        try:
                            select_email = panel.find_element(By.XPATH, ".//select[.//option[@value='EMAIL']]")
                            Select(select_email).select_by_value('EMAIL')
                            TaskFillPortalForm.log_and_print("  SELECT: forzado a 'EMAIL' para validación por correo.")
                        except Exception:
                            pass    
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

            # Buscar y hacer clic en la imagen "Navegar en internet" por alt
            img_navegar_internet = panel.find_elements(By.CSS_SELECTOR, "img[alt='datawifi-35479']")
            for img in img_navegar_internet:
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", img)
                    driver.execute_script("arguments[0].click();", img)
                    TaskFillPortalForm.log_and_print("  IMAGEN 'Navegar en internet' clickeada por JS.")
                except Exception:
                    TaskFillPortalForm.log_and_print("  IMAGEN 'Navegar en internet' no se pudo clicar.")
            # --- FIN Botón "Navegar en internet" ---

            # --- Click en botón "Validar" si existe (envía el correo con el PIN) ---
            btn_validar_correo = panel.find_elements(By.CSS_SELECTOR, "button#validar_correo")
            if btn_validar_correo:
                try:
                    btn_validar_correo[0].click()
                    TaskFillPortalForm.log_and_print("  BOTÓN 'Validar': clickeado normalmente.")
                except Exception:
                    driver.execute_script("arguments[0].click();", btn_validar_correo[0])
                    TaskFillPortalForm.log_and_print("  BOTÓN 'Validar': clickeado por JS.")
                time.sleep(3)  # Esperar que el portal procese y envíe el correo
            # --- FIN Click botón Validar ---

            # --- NUEVO: Leer código Guerrilla Mail e ingresarlo en input#pin ---
            inputs_pin = panel.find_elements(By.CSS_SELECTOR, "input#pin")
            if inputs_pin and guerrilla_sid:
                TaskFillPortalForm.log_and_print("[Task] Campo PIN detectado, esperando código en correo temporal...")
                codigo = leer_codigo(guerrilla_sid, asunto_busqueda="Valida tu correo", espera=60)
                if codigo:
                    try:
                        inputs_pin[0].clear()
                        inputs_pin[0].send_keys(codigo)
                        TaskFillPortalForm.log_and_print(f"[Task] Código PIN ingresado correctamente: {codigo}")
                    except Exception:
                        driver.execute_script("arguments[0].value = arguments[1];", inputs_pin[0], codigo)
                        TaskFillPortalForm.log_and_print(f"[Task] Código PIN ingresado por JS: {codigo}")
                else:
                    TaskFillPortalForm.log_and_print("[Task] No se recibió código en el correo temporal, tiempo de espera agotado.")
#           --- FIN Leer código Guerrilla Mail ---            

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
            # --- FIN Botones continuar ---

        TaskFillPortalForm.log_and_print("\n[Screenplay] === FIN DILIGENCIAMIENTO DE ELEMENTOS ===\n")
        time.sleep(2)
