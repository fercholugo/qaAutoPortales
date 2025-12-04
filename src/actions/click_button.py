from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By

class ClickButton:
    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        button = driver.find_element(self.by, self.locator)
        # Esperar a que el botón esté habilitado
        while not button.is_enabled():
            import time
            time.sleep(1)
        button.click()
