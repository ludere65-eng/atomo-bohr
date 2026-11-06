# Imagen base ligera con Python
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y habilitar salida de buffer inmediata
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema mínimas requeridas por Matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY GUI.py ./

# Instalar la librería local en modo editable con las dependencias gráficas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[gui]"

# Exponer el puerto predeterminado de Streamlit
EXPOSE 8501

# Variables de entorno para que Streamlit se ejecute sin restricciones en contenedor
ENV STREAMLIT_SERVER_PORT=8501 \
    ENV_STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

# Comando por defecto para iniciar la vista web
CMD ["streamlit", "run", "GUI.py", "--server.port=8501", "--server.address=0.0.0.0"]