# Imagen única para todos los procesos Python del backend (productor, consumidor y, más adelante, la API).
# Cada servicio de compose.yaml la arranca con un comando distinto (enunciado §2 lo permite).
FROM python:3.12-slim

WORKDIR /app

# 1) Primero solo las dependencias: si no cambian, Docker reutiliza esta capa y el build es rápido
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Después el código
COPY src ./src

# Que los print/log salgan al momento en "docker compose logs" (sin búfer)
ENV PYTHONUNBUFFERED=1
