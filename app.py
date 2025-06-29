import os
import sys
import logging
import time
from flask import Flask, request, abort
from telebot import types
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importar el bot desde qr_bot.py
try:
    from qr_bot import bot, tiempo_inicio_bot
    logger.info("Bot importado correctamente desde qr_bot.py")
except ImportError as e:
    logger.error(f"Error al importar el bot: {e}")
    sys.exit(1)

# Obtener token de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("No se encontró el token de Telegram")
    sys.exit(1)

# Crear aplicación Flask
app = Flask(__name__)

# Ruta para el webhook de Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        logger.info(f"Webhook recibido: {json_string[:100]}...")  # Log primeros 100 caracteres
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        logger.warning(f"Recibida solicitud con content-type incorrecto: {request.headers.get('content-type')}")
        abort(403)

# Ruta para verificar que el servidor está en funcionamiento
@app.route('/', methods=['GET'])
def health_check():
    return 'El bot está funcionando correctamente'

# Configurar el webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not render_url:
        logger.error("No se encontró RENDER_EXTERNAL_URL en las variables de entorno")
        return 'Error: No se encontró la URL de Render. Configurando con URL manual...'
    
    webhook_url = f"{render_url}/{TELEGRAM_TOKEN}"
    webhook_url = webhook_url.replace('http://', 'https://')  # Forzar HTTPS
    
    try:
        # Eliminar cualquier webhook existente
        bot.remove_webhook()
        time.sleep(1)
        
        # Configurar el nuevo webhook
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook configurado en: {webhook_url}")
        
        # Verificar que el webhook se configuró correctamente
        webhook_info = bot.get_webhook_info()
        logger.info(f"Información del webhook: URL={webhook_info.url}, pendientes={webhook_info.pending_update_count}")
        
        return f'Webhook configurado correctamente en: {webhook_url}<br>Información: {webhook_info.url}'
    except Exception as e:
        logger.error(f"Error al configurar webhook: {e}")
        return f'Error al configurar webhook: {e}'

# Obtener información del webhook
@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        info = bot.get_webhook_info()
        result = {
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections
        }
        logger.info(f"Información del webhook: {result}")
        return result
    except Exception as e:
        logger.error(f"Error al obtener información del webhook: {e}")
        return f'Error: {e}'

# Eliminar webhook
@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    try:
        bot.remove_webhook()
        logger.info("Webhook eliminado correctamente")
        return 'Webhook eliminado correctamente'
    except Exception as e:
        logger.error(f"Error al eliminar webhook: {e}")
        return f'Error al eliminar webhook: {e}'

if __name__ == "__main__":
    # Obtener puerto del entorno o usar 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    
    # Configurar webhook automáticamente al iniciar
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        webhook_url = f"{render_url}/{TELEGRAM_TOKEN}"
        webhook_url = webhook_url.replace('http://', 'https://')
        
        # Eliminar cualquier webhook existente
        logger.info("Eliminando webhooks existentes...")
        bot.remove_webhook()
        time.sleep(1)
        
        # Configurar el nuevo webhook
        logger.info(f"Configurando webhook en: {webhook_url}")
        bot.set_webhook(url=webhook_url)
        
        # Verificar la configuración
        webhook_info = bot.get_webhook_info()
        logger.info(f"Webhook configurado: URL={webhook_info.url}, pendientes={webhook_info.pending_update_count}")
    else:
        # Si no tenemos la URL de Render, intentar usar una URL genérica
        logger.warning("No se encontró la URL de Render, intentando configurar webhook manualmente...")
        
        # Intentar obtener la URL de la variable de entorno WEBHOOK_URL
        webhook_url = os.environ.get('WEBHOOK_URL')
        if webhook_url:
            webhook_url = f"{webhook_url}/{TELEGRAM_TOKEN}"
            webhook_url = webhook_url.replace('http://', 'https://')
            
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook configurado manualmente en: {webhook_url}")
        else:
            logger.error("No se pudo configurar el webhook automáticamente. Configúralo manualmente visitando /set_webhook")
    
    # Iniciar servidor
    logger.info(f"Iniciando servidor en el puerto {port}...")
    app.run(host="0.0.0.0", port=port) 