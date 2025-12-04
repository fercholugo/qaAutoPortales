from src.abilities.browse_the_web import BrowseTheWeb

class IsOnGoogle:
    """
    Question Screenplay: ¿Está el actor en la página de Google?
    Retorna True si la URL actual contiene 'google.com'.
    """
    @staticmethod
    def answered_by(actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        return "google.com" in driver.current_url
