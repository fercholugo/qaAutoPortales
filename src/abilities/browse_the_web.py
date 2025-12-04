from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import os

class BrowseTheWeb:
    def __init__(self, browser_name="chrome"):
        self.browser_name = browser_name.lower()
        self.driver = self._init_driver()

    def _init_driver(self):
        if self.browser_name == "chrome":
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Intenta usar ChromeDriver del sistema (Docker) o webdriver-manager (local)
            chromedriver_path = os.environ.get("CHROMEDRIVER_BIN")
            if chromedriver_path and os.path.exists(chromedriver_path):
                # Usa el ChromeDriver del sistema (en Docker con Chromium)
                chrome_options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
                service = Service(chromedriver_path)
            else:
                # Usa webdriver-manager para descargar automáticamente (en local)
                service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            
            return webdriver.Chrome(service=service, options=chrome_options)
        elif self.browser_name == "firefox":
            return webdriver.Firefox()
        elif self.browser_name == "edge":
            return webdriver.Edge()
        elif self.browser_name == "safari":
            options = None
            try:
                driver = webdriver.Safari()
                import time
                time.sleep(1)
                return driver
            except Exception as e:
                print("[Safari WebDriver] Error al iniciar Safari: ", e)
                raise
        else:
            raise ValueError(f"Navegador no soportado: {self.browser_name}")

    def quit(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(f"[WebDriver] Error al cerrar el navegador: {e}")