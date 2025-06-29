import os
import sys
import time
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Verificar que estamos en el directorio correcto
if not os.path.exists('qr_bot.py'):
    logger.error("Error: No se encontró el archivo qr_bot.py")
    logger.error("Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
    sys.exit(1)

# Cargar variables de entorno
try:
    load_dotenv()
    logger.info("Variables de entorno cargadas")
except Exception as e:
    logger.warning(f"No se pudieron cargar las variables de entorno: {e}")

# Verificar variables de entorno críticas
if not os.getenv('TELEGRAM_BOT_TOKEN'):
    logger.error("ERROR: No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno")
    sys.exit(1)

# Importar el bot después de verificar el entorno
try:
    from qr_bot import bot, tiempo_inicio_bot
    logger.info("Módulo del bot importado correctamente")
except ImportError as e:
    logger.error(f"Error al importar el módulo del bot: {e}")
    sys.exit(1)

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