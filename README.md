# Bot de Telegram para Lectura de Códigos QR

Este proyecto contiene un bot de Telegram para leer códigos QR y extraer nombres de personas.

## Funcionalidades

- Lectura de códigos QR desde imágenes
- Extracción de nombres usando expresiones regulares
- Mejora de la detección usando la API de Google Gemini
- Soporte para modos polling y webhook

## Despliegue en Render

Este proyecto está configurado para ser desplegado en Render:

### Opción 1: Despliegue automático con Blueprint

1. Crea una cuenta en [Render](https://render.com/)
2. Conecta tu repositorio de GitHub
3. Haz clic en "Blueprint" y selecciona este repositorio
4. Render desplegará automáticamente el bot según la configuración en `render.yaml`

### Opción 2: Despliegue manual

Puedes elegir entre dos modos de funcionamiento:

#### Opción A: Bot con Polling (Background Worker)
1. Crea un nuevo "Background Worker" en Render
2. Conecta tu repositorio
3. Configura:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run_telegram_bot.py`
   - Variables de entorno:
     - `TELEGRAM_BOT_TOKEN`: Tu token del bot de Telegram
     - `GEMINI_API_KEY`: Tu API key de Google Gemini

#### Opción B: Bot con Webhook (Web Service)
1. Crea un nuevo "Web Service" en Render
2. Conecta el mismo repositorio
3. Configura:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python qr_bot.py`
   - Variables de entorno:
     - `TELEGRAM_BOT_TOKEN`: Tu token del bot de Telegram
     - `GEMINI_API_KEY`: Tu API key de Google Gemini

### Configuración del Webhook de Telegram

Si eliges la opción de webhook, una vez desplegado el servicio, configura el webhook con:
```
https://api.telegram.org/bot{TU_TOKEN}/setWebhook?url=https://{TU_WEBHOOK_URL}/webhook
```

## Variables de Entorno Requeridas

- `TELEGRAM_BOT_TOKEN`: Token del bot de Telegram
- `GEMINI_API_KEY`: API key de Google Gemini (opcional, para mejorar la detección)

## ¿Qué opción elegir?

- **Polling (Background Worker)**: Más simple, pero consume más recursos. Ideal para bots con poco tráfico.
- **Webhook (Web Service)**: Más eficiente, solo se activa cuando recibe mensajes. Recomendado para producción.