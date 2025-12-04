from selenium.webdriver.common.by import By

def detect_form_elements(driver):
    # CAMBIO: Buscar todos los paneles cuyo id empieza por "panel"
    panels = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'panel')]")
    if not panels:
        print("[Screenplay] No se encontraron paneles con id que empiece por 'panel'.")
        print("[Screenplay] HTML actual:")
        print(driver.page_source)
        return

    # CAMBIO: Recorrer cada panel encontrado
    for panel in panels:
        panel_id = panel.get_attribute("id")
        print(f"\n[Utils] === DETECCIÓN DE ELEMENTOS DEL PANEL {panel_id} ===")
        print(f"Panel id={panel_id} encontrado.\n")
        # Inputs (todos los tipos)
        inputs = panel.find_elements(By.TAG_NAME, "input")
        for input_element in inputs:
            input_id = input_element.get_attribute('id')
            # Evitar duplicar el checkbox de términos y condiciones
            if input_id == 'label_terminos_condiciones':
                continue
            print("  INPUT:")
            print(f"    type: {input_element.get_attribute('type')}")
            print(f"    name: {input_element.get_attribute('name')}")
            print(f"    id: {input_id}")
            print(f"    class: {input_element.get_attribute('class')}")
            print(f"    aria-label: {input_element.get_attribute('aria-label')}")
            print(f"    placeholder: {input_element.get_attribute('placeholder')}")
            print(f"    title: {input_element.get_attribute('title')}")
            print(f"    enabled: {input_element.is_enabled()}")
            print(f"    displayed: {input_element.is_displayed()}")
        # Detección explícita del checkbox de términos y condiciones
        try:
            checkbox = panel.find_element(By.ID, "label_terminos_condiciones")
            print("  INPUT (Checkbox Términos y Condiciones - ESPECÍFICO):")
            print(f"    type: {checkbox.get_attribute('type')}")
            print(f"    name: {checkbox.get_attribute('name')}")
            print(f"    id: {checkbox.get_attribute('id')}")
            print(f"    class: {checkbox.get_attribute('class')}")
            print(f"    aria-label: {checkbox.get_attribute('aria-label')}")
            print(f"    placeholder: {checkbox.get_attribute('placeholder')}")
            print(f"    title: {checkbox.get_attribute('title')}")
            print(f"    enabled: {checkbox.is_enabled()}")
            print(f"    displayed: {checkbox.is_displayed()}")
            print(f"    selected: {checkbox.is_selected()}")
        except Exception:
            print("  [Screenplay] No se encontró el checkbox de términos y condiciones por id='label_terminos_condiciones'.")
        # Selects
        select_elements = panel.find_elements(By.TAG_NAME, 'select')
        for select_element in select_elements:
            print("  SELECT:")
            print(f"    name: {select_element.get_attribute('name')}")
            print(f"    id: {select_element.get_attribute('id')}")
            print(f"    aria-label: {select_element.get_attribute('aria-label')}")
            print(f"    placeholder: {select_element.get_attribute('placeholder')}")
            print(f"    enabled: {select_element.is_enabled()}")
            print(f"    displayed: {select_element.is_displayed()}")
            # Listar opciones del select
            options = select_element.find_elements(By.TAG_NAME, 'option')
            print(f"    opciones:")
            for idx, option in enumerate(options):
                print(f"      [{idx}] value: '{option.get_attribute('value')}', text: '{option.text}'")
        # Textareas
        text_areas = panel.find_elements(By.TAG_NAME, 'textarea')
        for text_area in text_areas:
            print("  TEXTAREA:")
            print(f"    name: {text_area.get_attribute('name')}")
            print(f"    id: {text_area.get_attribute('id')}")
            print(f"    aria-label: {text_area.get_attribute('aria-label')}")
            print(f"    placeholder: {text_area.get_attribute('placeholder')}")
            print(f"    enabled: {text_area.is_enabled()}")
            print(f"    displayed: {text_area.is_displayed()}")
        # Botones continuar
        buttons = panel.find_elements(By.CLASS_NAME, 'continuar')
        for button in buttons:
            print("  BOTÓN CONTINUAR:")
            print(f"    text: {button.text}")
            print(f"    enabled: {button.is_enabled()}")
            print(f"    displayed: {button.is_displayed()}")
        print(f"\n[Utils] === FIN DETECCIÓN DE ELEMENTOS DEL PANEL {panel_id} ===\n")
