from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By

class SelectInputsText:
    def __init__(self, by, locator, text):
        self.by = by
        self.locator = locator
        self.text = text

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        field = driver.find_element(self.by, self.locator)
        field.clear()
        field.send_keys(self.text)
