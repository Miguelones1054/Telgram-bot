import os
import sys
import time
import logging
from qr_bot import bot, tiempo_inicio_bot

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Bot de Telegram iniciado...")
    
    max_retries = 10
    retry_count = 0
    retry_delay = 5  # segundos
    
    while retry_count < max_retries:
        try:
            logger.info(f"Intento de conexión {retry_count + 1}/{max_retries}")
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=30)
            # Si llegamos aquí, el polling terminó sin error
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Error en el polling: {e}")
            logger.info(f"Reintentando en {retry_delay} segundos...")
            time.sleep(retry_delay)
            # Incrementar el tiempo de espera para el próximo reintento (máximo 60 segundos)
            retry_delay = min(retry_delay * 1.5, 60)
    
    if retry_count >= max_retries:
        logger.critical("Número máximo de reintentos alcanzado. El bot se detendrá.")
        sys.exit(1) 