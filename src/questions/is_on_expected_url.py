from src.abilities.browse_the_web import BrowseTheWeb

class IsOnExpectedUrl:
    """
    Question Screenplay: ¿Está el actor en la URL esperada?
    Retorna True si la URL actual contiene la URL esperada.
    """
    EXPECTED_URLS =[
        # Agrega aquí otras URLs finales válidas según tus portales
        "https://www.google.com/",
        "https://www.google.com.co/",
        "https://securelogin.hpe.com/swarm.cgi",
        "https://app.datawifi.co/easyfi/web/services/logindw.php"
    ]
    
    @staticmethod
    def answered_by(actor):
        browser = actor.ability_to(BrowseTheWeb)
        driver = browser.driver
        current_url = driver.current_url
        return any(current_url.startswith(url) for url in IsOnExpectedUrl.EXPECTED_URLS)
    

    