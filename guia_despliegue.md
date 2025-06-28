# Guía para desplegar el Bot de Telegram en Render como Web Service

Esta guía te mostrará paso a paso cómo desplegar tu bot de Telegram en Render utilizando el modo webhook (Web Service).

## Requisitos previos

1. Una cuenta en [Render](https://render.com/)
2. Un token de bot de Telegram (obtenido a través de [@BotFather](https://t.me/BotFather))
3. Una API key de Google Gemini (opcional, para mejorar la detección)
4. Tu código subido a un repositorio de GitHub

## Pasos para el despliegue

### 1. Preparar tu repositorio

Asegúrate de que tu repositorio contenga estos archivos esenciales:
- `qr_bot.py` - El código principal del bot
- `requirements.txt` - Las dependencias del proyecto
- `Procfile` - Configuración para Render (debe contener: `web: python qr_bot.py`)

### 2. Crear un nuevo Web Service en Render

1. Inicia sesión en tu cuenta de [Render](https://render.com/)
2. Haz clic en el botón "New +" en la esquina superior derecha
3. Selecciona "Web Service" de las opciones disponibles

### 3. Conectar tu repositorio

1. Selecciona el proveedor donde está alojado tu repositorio (GitHub, GitLab, etc.)
2. Busca y selecciona tu repositorio con el bot de Telegram
3. Haz clic en "Connect"

### 4. Configurar el servicio

En la página de configuración, establece los siguientes valores:

- **Name**: Un nombre para tu servicio (por ejemplo, "telegram-qr-bot")
- **Environment**: Selecciona "Python"
- **Region**: Elige la región más cercana a tus usuarios
- **Branch**: La rama de tu repositorio que deseas desplegar (normalmente "main" o "master")
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python qr_bot.py`

### 5. Configurar variables de entorno

1. Desplázate hacia abajo hasta la sección "Environment Variables"
2. Haz clic en "Add Environment Variable"
3. Añade las siguientes variables:
   - `TELEGRAM_BOT_TOKEN`: Tu token del bot de Telegram
   - `GEMINI_API_KEY`: Tu API key de Google Gemini (opcional)

### 6. Opciones de plan

1. Selecciona el plan que deseas usar (puedes comenzar con el plan gratuito)
2. Haz clic en "Create Web Service"

### 7. Esperar a que se complete el despliegue

Render comenzará a construir y desplegar tu servicio. Este proceso puede tardar unos minutos. Puedes seguir el progreso en los logs que se muestran.

### 8. Configurar el webhook de Telegram

Una vez que el despliegue esté completo:

1. Copia la URL de tu servicio en Render (algo como `https://tu-servicio.onrender.com`)
2. Abre tu navegador y accede a la siguiente URL (reemplazando con tus propios valores):
   ```
   https://api.telegram.org/bot{TU_TOKEN_DE_TELEGRAM}/setWebhook?url=https://{TU_URL_DE_RENDER}/webhook
   ```

3. Deberías recibir una respuesta similar a:
   ```json
   { "ok": true, "result": true, "description": "Webhook was set" }
   ```

### 9. Verificar que el bot funcione

1. Abre Telegram y busca tu bot
2. Envía un mensaje o una imagen con un código QR
3. El bot debería responder procesando la imagen

## Solución de problemas

Si tu bot no responde:

1. Verifica los logs en Render para detectar errores
2. Asegúrate de que el webhook esté configurado correctamente
3. Verifica que las variables de entorno estén configuradas correctamente
4. Comprueba que el bot esté activo en Telegram

## Mantenimiento

- Render automáticamente desplegará nuevas versiones cuando hagas push a tu repositorio
- Puedes monitorear el rendimiento y los logs desde el panel de control de Render

¡Listo! Tu bot de Telegram ahora está desplegado como un servicio web en Render y responderá a los mensajes a través del webhook. 