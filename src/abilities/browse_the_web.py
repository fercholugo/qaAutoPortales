from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import subprocess
import time
import requests

class BrowseTheWeb:
    def __init__(self, browser_name="chrome"):
        self.browser_name = browser_name.lower()
        self._chromedriver_process = None
        self.driver = self._init_driver()

    def _init_driver(self):
        if self.browser_name == "chrome":
            chrome_options = Options()

            # Solo headless cuando existe el chromedriver de sistema (imagen Docker/Railway).
            # No usar /.dockerenv: en el runtime real de Railway ese archivo no existe,
            # aunque sí estemos en un contenedor, y eso hacía caer siempre a la rama local.
            if os.path.exists(os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")):
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")

                # Lanzamos chromedriver como proceso independiente en vez de dejar
                # que Selenium Service lo gestione: ese camino falla siempre con
                # "DevToolsActivePort file doesn't exist" en este contenedor,
                # mientras que chromedriver standalone + Remote funciona consistentemente.
                chromedriver_bin = os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")
                port = 9515
                print(f"[BrowseTheWeb] Lanzando chromedriver: {chromedriver_bin} --port={port}", flush=True)
                self._chromedriver_process = subprocess.Popen([chromedriver_bin, f"--port={port}"])
                print(f"[BrowseTheWeb] chromedriver PID: {self._chromedriver_process.pid}", flush=True)

                listo = False
                for intento in range(30):
                    if self._chromedriver_process.poll() is not None:
                        raise RuntimeError(
                            f"chromedriver murió antes de responder (código {self._chromedriver_process.returncode})"
                        )
                    try:
                        requests.get(f"http://localhost:{port}/status", timeout=1)
                        listo = True
                        print(f"[BrowseTheWeb] chromedriver listo tras {intento} intentos", flush=True)
                        break
                    except requests.exceptions.ConnectionError:
                        time.sleep(0.5)

                if not listo:
                    raise RuntimeError("chromedriver no respondio en /status tras 15s")

                print("[BrowseTheWeb] Conectando webdriver.Remote...", flush=True)
                driver = webdriver.Remote(command_executor=f"http://localhost:{port}", options=chrome_options)
                print("[BrowseTheWeb] Sesion de Chrome creada OK", flush=True)
                return driver
            else:
                # En local: usa webdriver-manager para descargar el driver correcto automáticamente
                service = Service(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=chrome_options)
        elif self.browser_name == "firefox":
            return webdriver.Firefox()
        elif self.browser_name == "edge":
            return webdriver.Edge()
        elif self.browser_name == "safari":
            options = None
            try:
                driver = webdriver.Safari()
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
        finally:
            if self._chromedriver_process:
                self._chromedriver_process.terminate()