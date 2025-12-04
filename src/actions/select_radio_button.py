from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By

class SelectRadioButton:
    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        radio = driver.find_element(self.by, self.locator)
        if not radio.is_selected():
            driver.execute_script("arguments[0].click();", radio)
