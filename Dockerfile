# Imagen base: Python 3.12 slim (ligera)
FROM python:3.12-slim

# Establece directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para Chrome, Selenium e imageio
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements.txt e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto completo
COPY . .

# Crea directorio para reportes y videos (se sobreescribe con volumen en Railway)
RUN mkdir -p reporte_html/videos_ejecuciones

# Variables de entorno para Chrome headless en contenedor
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Arranca el servidor web; Railway inyecta PORT automáticamente
CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8000}"]