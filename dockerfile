# Imagen base
FROM python:3.10

# Copiar los archivos de la aplicación
COPY . /app
WORKDIR /app

# Instalar las dependencias
RUN pip install -r requirements.txt

# Exponer el puerto que usa la aplicación
EXPOSE 8000

# Iniciar la aplicación al arrancar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
