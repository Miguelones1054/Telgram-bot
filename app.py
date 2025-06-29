import os
import base64
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from qr_scanner import procesar_imagen_qr
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener el token desde las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("No se encontró el token de Telegram. Asegúrate de tener la variable TELEGRAM_TOKEN en el archivo .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    # Obtén la mejor calidad de la foto
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()

    # Procesa la imagen con la función existente
    resultado = procesar_imagen_qr(file_bytes)
    
    # Solo responder si se detectó un QR válido
    if resultado and "contenido_qr" in resultado:
        msg = f"✅ QR detectado!\n\n"
        msg += f"👤 *Nombre:* {resultado.get('nombre', 'N/A')}\n"
        msg += f"📍 *Dirección:* {resultado.get('direccion', 'N/A')}\n"
        msg += f"🏙️ *Ciudad:* {resultado.get('ciudad', 'N/A')}\n"
        msg += f"📱 *Numero Nequi (solo para QR personales):* {resultado.get('celular', 'N/A')}\n"
        if resultado.get('tipo_contenido'):
            msg += f"📝 *Tipo:* {resultado.get('tipo_contenido')}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot de Telegram iniciado. Esperando imágenes...")
    app.run_polling(drop_pending_updates=True) 