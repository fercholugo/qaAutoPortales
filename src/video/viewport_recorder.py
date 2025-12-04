import os
import io
import time
import threading
import imageio.v2 as imageio


class ViewportRecorder:
    """
    Grabador básico de video del viewport vía screenshots.
    - Captura un frame cada 'interval' segundos.
    - Ensambla el video en tiempo real usando imageio.
    """

    def __init__(self, driver, output_path, interval=0.5):
        """
        Inicializa el recorder.

        Args:
            driver: Instancia de Selenium WebDriver.
            output_path: Ruta del archivo MP4 a generar.
            interval: Segundos entre capturas (0.3 ≈ 3 fps).
        """
        self.driver = driver
        self.output_path = output_path
        self.interval = float(interval)
        self._running = False
        self._thread = None
        self._writer = None

    @staticmethod
    def ensure_dir(path: str):
        """Crea el directorio de salida si no existe."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def start(self):
        """Inicia el hilo de captura periódica."""
        if self._running:
            return
        self.ensure_dir(self.output_path)

        # FPS aproximado según el intervalo (mínimo 1).
        fps = max(1, int(round(1 / self.interval)))

        # Abre el writer del video.
        self._writer = imageio.get_writer(self.output_path, fps=fps)
        self._running = True

        # Lanza el hilo que captura frames a intervalos regulares.
        self._thread = threading.Thread(
            target=self._loop, name="ViewportRecorder", daemon=True
        )
        self._thread.start()

    def _loop(self):
        """Bucle del hilo: captura y agrega frames mientras esté activo."""
        while self._running:
            try:
                # Captura screenshot en PNG y lo convierte a frame.
                png_bytes = self.driver.get_screenshot_as_png()
                frame = imageio.imread(io.BytesIO(png_bytes))
                # Agrega el frame al video.
                self._writer.append_data(frame)
            except Exception:
                # Ignora fallos puntuales de captura para no interrumpir el test.
                pass
            # Espera el intervalo configurado antes del próximo frame.
            time.sleep(self.interval)

    def stop(self):
        """Detiene la captura y cierra los recursos del writer."""
        if not self._running:
            return

        self._running = False

        if self._thread:
            self._thread.join(timeout=3)

        try:
            if self._writer:
                self._writer.close()
        finally:
            self._writer = None
            self._thread = None