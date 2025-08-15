import os
import base64
import logging
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from qr_scanner import procesar_imagen_qr
from dotenv import load_dotenv
from io import BytesIO
import unicodedata

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

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

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
        await update.message.reply_text(
            text=msg,
            parse_mode="Markdown",
            reply_to_message_id=update.message.message_id
        )

async def handle_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return  # Ignora updates que no son mensajes de texto normales

    mensaje = update.message.text
    mensaje_normalizado = normalizar(mensaje)
    patron = r"comprobante\s*para\s*(.+?)\s*de\s*(\d+)\s*al\s*numero\s*(\d+)"
    coincidencia = re.match(patron, mensaje_normalizado, re.IGNORECASE)
    if coincidencia:
        # Extraer los mismos grupos del mensaje original usando los índices del match en el mensaje normalizado y mapearlo al mensaje original
        # Para esto, se puede usar re.finditer para encontrar la posición del nombre en el mensaje normalizado y mapearlo al mensaje original
        # Pero como el patrón es estricto, podemos usar split para obtener el nombre original
        partes = re.split(r"de\s*\d+\s*al\s*numero\s*\d+", mensaje_normalizado)
        if len(partes) > 0:
            # Encuentra el inicio del nombre en el mensaje original
            idx_inicio = mensaje.lower().find('para')
            if idx_inicio != -1:
                idx_inicio += len('para')
                # Busca el 'de' después del nombre
                idx_de = mensaje.lower().find('de', idx_inicio)
                if idx_de != -1:
                    recipient = mensaje[idx_inicio:idx_de].strip()
                else:
                    recipient = coincidencia.group(1)  # fallback
            else:
                recipient = coincidencia.group(1)  # fallback
        else:
            recipient = coincidencia.group(1)  # fallback
        amount = coincidencia.group(2)
        phone = coincidencia.group(3)

        payload = {
            "tipo": "bot",
            "datos": {
                "recipient": recipient,
                "amount": amount,
                "phone": phone
            }
        }
        API_URL = os.getenv("API_COMPROBANTE_URL", "https://nequifrontx.onrender.com/generate_image/")
        try:
            respuesta = requests.post(API_URL, json=payload)
            if respuesta.status_code == 200:
                imagen = BytesIO(respuesta.content)
                imagen.name = "comprobante.png"
                await update.message.reply_photo(photo=imagen)
            else:
                await update.message.reply_text("Error generando el comprobante. Intenta más tarde.")
        except Exception as e:
            await update.message.reply_text(f"Ocurrió un error: {e}")
    # No else: este handler solo responde si el mensaje tiene el formato correcto

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para obtener el ID del chat actual"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    message = f"ℹ️ Información del chat:\n\n"
    message += f"📌 ID: `{chat_id}`\n"
    message += f"📝 Tipo: {chat_type}\n"
    
    if update.effective_user:
        user_id = update.effective_user.id
        message += f"👤 Tu ID de usuario: `{user_id}`"
    
    await update.message.reply_text(
        text=message,
        parse_mode="Markdown"
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Recargar cuenta", callback_data="recargar_cuenta"),
            InlineKeyboardButton("Comprar usuario", callback_data="comprar_usuario")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "recargar_cuenta":
        await query.edit_message_text(text="Has elegido *Recargar cuenta*.", parse_mode="Markdown")
    elif query.data == "comprar_usuario":
        await query.edit_message_text(text="Has elegido *Comprar usuario*.", parse_mode="Markdown")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_comprobante))
    app.add_handler(CommandHandler("id", get_chat_id))
    app.add_handler(CommandHandler("menu", menu_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot de Telegram iniciado. Esperando imágenes...")
    app.run_polling(drop_pending_updates=True) 