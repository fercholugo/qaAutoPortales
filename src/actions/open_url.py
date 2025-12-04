from src.abilities.browse_the_web import BrowseTheWeb

class OpenUrl:
    def __init__(self, url):
        self.url = url

    def perform_as(self, actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        driver.get(self.url)
