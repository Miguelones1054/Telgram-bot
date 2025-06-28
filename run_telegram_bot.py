import os
import sys
import time
from qr_bot import bot, tiempo_inicio_bot

if __name__ == "__main__":
    print("Bot de Telegram iniciado...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 