# Despliegue en Railway

Este documento explica cómo desplegar esta aplicación en Railway.

## Requisitos

1. Tener una cuenta en [Railway](https://railway.app/)
2. Tener el código en un repositorio de GitHub

## Pasos para el despliegue

### 1. Preparar el repositorio

Asegúrate de que tu repositorio contiene los siguientes archivos:
- `app.py` - La aplicación Flask
- `qr_scanner.py` - El módulo de escaneo de QR
- `requirements.txt` - Las dependencias de Python
- `Dockerfile` - Configuración de Docker
- `.railway.toml` - Configuración específica para Railway
- `templates/` - Directorio con las plantillas HTML

### 2. Conectar Railway a GitHub

1. Inicia sesión en [Railway](https://railway.app/)
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu cuenta de GitHub y selecciona el repositorio

### 3. Configurar el proyecto

1. Una vez creado el proyecto, ve a la pestaña "Variables"
2. Añade la variable de entorno `GEMINI_API_KEY` si utilizas la API de Google Gemini
3. Ve a la pestaña "Settings" y asegúrate de que:
   - El directorio raíz está configurado correctamente
   - Railway detectó automáticamente el Dockerfile

### 4. Desplegar

1. Railway detectará automáticamente el Dockerfile y lo construirá
2. Una vez completada la construcción, la aplicación se desplegará automáticamente
3. Haz clic en la URL generada para acceder a tu aplicación

### 5. Configurar dominio personalizado (opcional)

1. Ve a la pestaña "Settings"
2. En la sección "Domains", puedes configurar un dominio personalizado

## Solución de problemas

Si encuentras problemas durante el despliegue:

### Error de construcción con numpy o dependencias

Si ves errores relacionados con la construcción de numpy o falta de módulos como 'distutils':

1. Verifica que el Dockerfile incluya las dependencias necesarias:
   ```
   RUN apt-get update && apt-get install -y \
       libzbar0 \
       libzbar-dev \
       python3-distutils \
       python3-dev \
       build-essential
   ```

2. Asegúrate de que requirements.txt use versiones compatibles:
   ```
   numpy==1.23.5
   pillow==9.5.0
   ```

### Error de permisos en el directorio uploads

Si la aplicación no puede escribir en el directorio uploads:

1. Verifica que el Dockerfile cree el directorio:
   ```
   RUN mkdir -p uploads
   ```

2. Asegúrate de que los permisos sean correctos:
   ```
   RUN mkdir -p uploads && chmod 777 uploads
   ```

### Problemas con las variables de entorno

Si la aplicación no puede acceder a las variables de entorno:

1. Verifica que estén correctamente configuradas en Railway
2. Asegúrate de que la aplicación las carga correctamente con python-dotenv

## Recursos adicionales

- [Documentación de Railway](https://docs.railway.app/)
- [Guía de Docker en Railway](https://docs.railway.app/deploy/docker)
- [Solución de problemas comunes](https://docs.railway.app/troubleshoot/common-issues) 