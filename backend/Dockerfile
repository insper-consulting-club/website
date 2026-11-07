FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema para o Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Produção: aplica migrations, prepara os arquivos estáticos e inicia o
# servidor (gunicorn). PORT é definida pela hospedagem; localmente, 8000.
# No desenvolvimento local, o docker-compose.yml substitui este comando.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]