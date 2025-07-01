import os
import base64
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from qr_scanner import procesar_imagen_qr
from dotenv import load_dotenv
from whitelist import Whitelist

# Cargar variables de entorno
load_dotenv()

# Obtener el token desde las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ID del administrador del bot

if not TELEGRAM_TOKEN:
    raise ValueError("No se encontró el token de Telegram. Asegúrate de tener la variable TELEGRAM_TOKEN en el archivo .env")

if ADMIN_ID == 0:
    raise ValueError("No se encontró el ID del administrador. Asegúrate de tener la variable ADMIN_ID en el archivo .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Inicializar la lista blanca
whitelist = Whitelist()
# Asegurarse de que el admin esté en la lista blanca
whitelist.add_id(ADMIN_ID)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si el usuario/grupo está autorizado
    chat_id = update.effective_chat.id
    if not whitelist.is_authorized(chat_id):
        await update.message.reply_text(
            "❌ No autorizado\n"
            "Solo disponible en el grupo de telegram @NequiAlpha01\n"
            "Bot creado por @Neonova_Ui",
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True
        )
        return

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

async def add_to_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si el comando lo envía el administrador
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Solo el administrador puede usar este comando.")
        return

    try:
        # Obtener el ID del argumento del comando
        if not context.args:
            await update.message.reply_text("❌ Por favor, proporciona el ID del chat a autorizar.")
            return
        
        chat_id = int(context.args[0])
        whitelist.add_id(chat_id)
        await update.message.reply_text(f"✅ Chat ID {chat_id} ha sido autorizado exitosamente.")
    except ValueError:
        await update.message.reply_text("❌ Por favor, proporciona un ID válido.")

async def remove_from_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar si el comando lo envía el administrador
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Solo el administrador puede usar este comando.")
        return

    try:
        # Obtener el ID del argumento del comando
        if not context.args:
            await update.message.reply_text("❌ Por favor, proporciona el ID del chat a remover.")
            return
        
        chat_id = int(context.args[0])
        if chat_id == ADMIN_ID:
            await update.message.reply_text("❌ No puedes remover al administrador de la lista blanca.")
            return
            
        whitelist.remove_id(chat_id)
        await update.message.reply_text(f"✅ Chat ID {chat_id} ha sido removido de la lista de autorizados.")
    except ValueError:
        await update.message.reply_text("❌ Por favor, proporciona un ID válido.")

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

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CommandHandler("autorizar", add_to_whitelist))
    app.add_handler(CommandHandler("remover", remove_from_whitelist))
    app.add_handler(CommandHandler("id", get_chat_id))
    print("Bot de Telegram iniciado. Esperando imágenes...")
    app.run_polling(drop_pending_updates=True) 