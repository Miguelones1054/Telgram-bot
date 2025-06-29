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
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
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
        return 'Error: No se encontró la URL de Render'
    
    webhook_url = f"{render_url}/{TELEGRAM_TOKEN}"
    webhook_url = webhook_url.replace('http://', 'https://')  # Forzar HTTPS
    
    try:
        # Eliminar cualquier webhook existente
        bot.remove_webhook()
        time.sleep(1)
        
        # Configurar el nuevo webhook
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook configurado en: {webhook_url}")
        return f'Webhook configurado correctamente en: {webhook_url}'
    except Exception as e:
        logger.error(f"Error al configurar webhook: {e}")
        return f'Error al configurar webhook: {e}'

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
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook configurado en: {webhook_url}")
    else:
        logger.warning("No se encontró la URL de Render, no se pudo configurar el webhook automáticamente")
    
    # Iniciar servidor
    logger.info(f"Iniciando servidor en el puerto {port}...")
    app.run(host="0.0.0.0", port=port) 