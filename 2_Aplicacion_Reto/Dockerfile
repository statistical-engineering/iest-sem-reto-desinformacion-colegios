# Imagen mínima: solo Python (el servidor no usa librerías externas).
# Sirve en Render, Fly.io, Railway, Koyeb, etc.
FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED=1 RETO_HOSTING=1 RETO_DATOS=/data
EXPOSE 8000
CMD ["python", "servidor.py"]
