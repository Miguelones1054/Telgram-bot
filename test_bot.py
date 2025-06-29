import os
import sys
import time
import logging
from qr_bot import bot

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_bot():
    """Prueba el bot en modo polling localmente"""
    logger.info("Iniciando prueba del bot en modo polling...")
    
    # Eliminar cualquier webhook configurado
    logger.info("Eliminando webhooks existentes...")
    bot.remove_webhook()
    time.sleep(1)
    
    # Verificar que el webhook se eliminó correctamente
    webhook_info = bot.get_webhook_info()
    logger.info(f"Webhook eliminado: URL={webhook_info.url}")
    
    # Iniciar polling
    logger.info("Iniciando polling...")
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en polling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_bot() 