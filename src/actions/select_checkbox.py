from src.abilities.browse_the_web import BrowseTheWeb
from selenium.webdriver.common.by import By

class SelectCheckbox:
    def __init__(self, by, locator, check=True):
        self.by = by
        self.locator = locator
        self.check = check  # True para marcar, False para desmarcar

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        checkbox = driver.find_element(self.by, self.locator)
        if checkbox.is_selected() != self.check:
            driver.execute_script("arguments[0].click();", checkbox)
