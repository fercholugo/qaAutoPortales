from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import random

class SelectDropdown:
    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        dropdown = driver.find_element(self.by, self.locator)
        select = Select(dropdown)
        # Filtrar opciones válidas (ignorando 'no_respuesta' y opciones con 'Selecciona')
        valid_options = [option for option in select.options 
                         if option.get_attribute('value') != 'no_respuesta' and 'Selecciona' not in option.text]
        if not valid_options:
            print('[Screenplay] No hay opciones válidas para seleccionar en el dropdown.')
            return
        selected_option = random.choice(valid_options)
        select.select_by_value(selected_option.get_attribute('value'))
        print(f"[Screenplay] Opción seleccionada en dropdown: value='{selected_option.get_attribute('value')}', text='{selected_option.text}'")
