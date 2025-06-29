import os
import sys
import telebot
from dotenv import load_dotenv
import re
import urllib.parse
from io import BytesIO
import time
import numpy as np
from PIL import Image
import google.generativeai as genai

# Configurar credenciales de Google desde variables de entorno (si es necesario)
if "GOOGLE_CREDENTIALS_JSON" in os.environ:
    import json
    try:
        with open("credentials.json", "w") as f:
            f.write(os.environ["GOOGLE_CREDENTIALS_JSON"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
        print("Archivo de credenciales de Google creado desde variable de entorno")
    except Exception as e:
        print(f"Error al crear archivo de credenciales: {e}")

# Cargar variables de entorno
try:
    load_dotenv()
except ImportError:
    print("Módulo python-dotenv no encontrado. Asegúrate de configurar los tokens manualmente.")

# Configurar token de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configurar API de Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Verificar token de Telegram
if not TELEGRAM_TOKEN:
    print("ERROR: No se encontró el token de Telegram en las variables de entorno.")
    print("Asegúrate de configurar TELEGRAM_BOT_TOKEN en las variables de entorno de Render.")
    sys.exit(1)

# Verificar API key de Gemini
if not GEMINI_API_KEY:
    print("ADVERTENCIA: No se encontró la API key de Google Gemini en las variables de entorno.")
    print("El análisis avanzado no estará disponible.")
else:
    # Configurar Gemini
    genai.configure(api_key=GEMINI_API_KEY)

# Crear instancia del bot de Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Registrar el tiempo de inicio del bot
tiempo_inicio_bot = int(time.time())

# Importar bibliotecas para QR
pyzbar_available = False
cv2_available = False

# Intentar importar múltiples bibliotecas para lectura de QR
print("Intentando cargar bibliotecas para lectura de QR...")

# 1. Intentar con pyzbar
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    pyzbar_available = True
    print("Biblioteca pyzbar cargada correctamente")
except ImportError as e:
    print(f"Error al cargar pyzbar: {e}")
    
    # Intentar instalar pyzbar automáticamente
    try:
        import subprocess
        print("Intentando instalar pyzbar...")
        subprocess.check_call(["pip", "install", "pyzbar"])
        from pyzbar.pyzbar import decode as pyzbar_decode
        pyzbar_available = True
        print("Biblioteca pyzbar instalada y cargada correctamente")
    except Exception as e:
        print(f"Error al instalar pyzbar: {e}")

# 2. Intentar con OpenCV como alternativa
if not pyzbar_available:
    try:
        print("Intentando cargar OpenCV como alternativa...")
        import cv2
        cv2_available = True
        print("OpenCV cargado correctamente")
    except ImportError:
        print("OpenCV no disponible")
        
        # Intentar instalar OpenCV
        try:
            import subprocess
            print("Intentando instalar OpenCV...")
            subprocess.check_call(["pip", "install", "opencv-python-headless"])
            import cv2
            cv2_available = True
            print("OpenCV instalado y cargado correctamente")
        except Exception as e:
            print(f"Error al instalar OpenCV: {e}")

if not pyzbar_available and not cv2_available:
    print("Error crítico: No se encontraron bibliotecas para leer QR.")
    print("Este bot requiere alguna de estas bibliotecas: pyzbar o OpenCV")
    print("En sistemas Linux, ejecuta: apt-get install libzbar0 zbar-tools")
    sys.exit(1)
else:
    print("Al menos una biblioteca para lectura de QR está disponible")

# Función para decodificar QR usando las bibliotecas disponibles
def decodificar_qr(imagen_bytes):
    try:
        # Convertir bytes a imagen
        img = Image.open(BytesIO(imagen_bytes))
        
        # 1. Intentar con pyzbar si está disponible
        if pyzbar_available:
            decoded_objects = pyzbar_decode(img)
            for obj in decoded_objects:
                decoded_text = obj.data.decode('utf-8')
                print(f"Contenido del QR (pyzbar): {decoded_text}")
                return decoded_text
                
            # Si no se encontró ningún QR, intentar con una imagen procesada
            img_gray = img.convert('L')
            img_contrast = Image.eval(img_gray, lambda x: 0 if x < 128 else 255)
            
            decoded_objects = pyzbar_decode(img_contrast)
            for obj in decoded_objects:
                decoded_text = obj.data.decode('utf-8')
                print(f"Contenido del QR (pyzbar - imagen procesada): {decoded_text}")
                return decoded_text
        
        # 2. Intentar con OpenCV si está disponible
        if cv2_available:
            # Convertir PIL a OpenCV
            img_array = np.array(img)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Crear detector QR
            qr_detector = cv2.QRCodeDetector()
            data, bbox, _ = qr_detector.detectAndDecode(img_cv)
            
            if data:
                print(f"Contenido del QR (OpenCV): {data}")
                return data
                
            # Intentar con imagen procesada
            img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
            data, bbox, _ = qr_detector.detectAndDecode(img_thresh)
            
            if data:
                print(f"Contenido del QR (OpenCV - imagen procesada): {data}")
                return data
        
        return None
    except Exception as e:
        print(f"Error al decodificar QR: {e}")
        return None

# Función para extraer nombres de personas del contenido del QR
def extraer_nombre(texto):
    # Buscar texto que aparezca después de un número de al menos 3 dígitos
    # y tomar ese texto hasta que aparezca otro número
    patron = r'(\d{3,})\s*([A-Z\s]+)(?=\d|$)'
    
    matches = re.findall(patron, texto)
    nombres_candidatos = []
    
    for match in matches:
        nombre = match[1].strip()
        if len(nombre) > 5:  # Filtrar nombres muy cortos
            nombres_candidatos.append(nombre)
    
    # Si encontramos candidatos, devolver el más largo
    if nombres_candidatos:
        return max(nombres_candidatos, key=len)
    
    return None

# Función para extraer direcciones del contenido del QR
def extraer_direccion(texto):
    # Buscar patrones comunes de direcciones colombianas
    # Patrón para calles, carreras, avenidas, etc.
    direccion_patterns = [
        r'(?:Cl|CL|Calle|CALLE|Cr|CR|Carrera|CARRERA|Av|AV|Avenida|AVENIDA|Dg|DG|Diagonal|DIAGONAL|Tv|TV|Transversal|TRANSVERSAL)\s+\d+[A-Za-z]?\s*(?:#|No\.?|número|N°)?\s*\d+[A-Za-z]?\s*-\s*\d+',
        r'(?:Cl|CL|Calle|CALLE|Cr|CR|Carrera|CARRERA|Av|AV|Avenida|AVENIDA|Dg|DG|Diagonal|DIAGONAL|Tv|TV|Transversal|TRANSVERSAL)\s+\d+[A-Za-z]?\s*(?:#|No\.?|número|N°)?\s*\d+[A-Za-z]?',
    ]
    
    # Buscar en todo el texto
    for pattern in direccion_patterns:
        match = re.search(pattern, texto, re.IGNORECASE)
        if match:
            return match.group(0)
    
    # Buscar después de identificadores comunes
    direccion_identificadores = ["DIRECCION:", "DIRECCIÓN:", "DIR:", "ADDRESS:", "DOMICILIO:"]
    for identificador in direccion_identificadores:
        if identificador in texto.upper():
            idx = texto.upper().find(identificador) + len(identificador)
            end_idx = texto.find("\n", idx) if "\n" in texto[idx:] else len(texto)
            direccion = texto[idx:end_idx].strip()
            if direccion:
                return direccion
    
    # Buscar patrón específico para el formato compartido
    # Ejemplo: 00020101021126180014Cl 1c # 19b-35...
    match = re.search(r'0+\d{6,}(\d{4})([A-Za-z]{2}\s+\d+[A-Za-z]?\s*#\s*\d+[A-Za-z]?-\d+)', texto)
    if match:
        return match.group(2)
    
    return None

# Función para extraer ciudades del contenido del QR
def extraer_ciudad(texto):
    # Lista de ciudades y municipios comunes de Colombia
    ciudades_comunes = [
        "BOGOTA", "BOGOTÁ", "MEDELLIN", "MEDELLÍN", "CALI", "BARRANQUILLA", "CARTAGENA", 
        "CUCUTA", "CÚCUTA", "BUCARAMANGA", "PEREIRA", "SANTA MARTA", "MANIZALES", 
        "VILLAVICENCIO", "PASTO", "MONTERIA", "MONTERÍA", "NEIVA", "ARMENIA", "POPAYAN", 
        "POPAYÁN", "SINCELEJO", "VALLEDUPAR", "IBAGUE", "IBAGUÉ", "TUNJA", "YOPAL", 
        "FLORENCIA", "QUIBDO", "QUIBDÓ", "RIOHACHA", "MOCOA", "ARAUCA", "LETICIA", 
        "INIRIDA", "INÍRIDA", "MITU", "MITÚ", "PUERTO CARREÑO", "SAN ANDRES", "SAN ANDRÉS",
        "MALAMBO", "SOLEDAD", "SOACHA", "BELLO", "ENVIGADO", "ITAGUI", "ITAGÜÍ", "JAMUNDI", 
        "JAMUNDÍ", "DOSQUEBRADAS", "FLORIDABLANCA", "GIRÓN", "PIEDECUESTA", "ZIPAQUIRA", 
        "ZIPAQUIRÁ", "FACATATIVA", "FACATATIVÁ", "FUSAGASUGA", "FUSAGASUGÁ", "CHIA", "CHÍA"
    ]
    
    # Buscar ciudades comunes en el texto
    for ciudad in ciudades_comunes:
        if ciudad in texto.upper():
            return ciudad
    
    # Buscar después de identificadores comunes
    ciudad_identificadores = ["CIUDAD:", "CITY:", "MUNICIPIO:", "LOCALIDAD:"]
    for identificador in ciudad_identificadores:
        if identificador in texto.upper():
            idx = texto.upper().find(identificador) + len(identificador)
            end_idx = texto.find("\n", idx) if "\n" in texto[idx:] else len(texto)
            ciudad = texto[idx:end_idx].strip()
            if ciudad:
                return ciudad
    
    # Buscar patrón específico para el formato compartido
    # Ejemplo: ...6007MALAMBO6221...
    match = re.search(r'600[0-9]([A-Z]+(?:,\s*[A-Z\.]+)?)', texto)
    if match:
        return match.group(1)
    
    # Buscar "BOGOTA, D.C." o similares
    match = re.search(r'([A-Z]+),\s*D\.?C\.?', texto)
    if match:
        return f"{match.group(0)}"
    
    return None

# Función para extraer números de celular del contenido del QR
def extraer_celular(texto):
    # Patrón específico para el formato compartido
    # Ejemplo: ...6221021031756877610703CEL...
    # Donde 3175687761 es el número de celular
    cel_pattern = r'62210210(\d{10})0703CEL'
    match = re.search(cel_pattern, texto)
    if match:
        numero = match.group(1)
        # Verificar que comienza con 3 (celulares colombianos)
        if numero.startswith('3') and len(numero) == 10:
            return numero
    
    # Buscar después de identificadores comunes
    celular_identificadores = ["CELULAR:", "CEL:", "MÓVIL:", "MOVIL:", "PHONE:", "TEL:"]
    for identificador in celular_identificadores:
        if identificador in texto.upper():
            idx = texto.upper().find(identificador) + len(identificador)
            # Buscar 10 dígitos consecutivos después del identificador
            match = re.search(r'(\d{10})', texto[idx:idx+20])
            if match and match.group(1).startswith('3'):
                return match.group(1)
    
    # Buscar cualquier número de 10 dígitos que comience con 3 (celulares colombianos)
    matches = re.findall(r'3\d{9}', texto)
    if matches:
        return matches[0]
    
    return None

# Función para analizar ciudad con Gemini
def analizar_ciudad_con_gemini(texto):
    try:
        if not GEMINI_API_KEY:
            return None
        
        # Crear modelo de Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Crear prompt para Gemini
        prompt = f"""
        Analiza el siguiente contenido de un código QR y extrae SOLO el nombre de la ciudad o municipio si está presente.
        
        Contenido del QR: "{texto}"
        
        Tu tarea es:
        1. Identificar si hay alguna ciudad o municipio mencionado en el texto
        2. Si encuentras una ciudad, devuelve solo el nombre de la ciudad, sin ningún texto adicional
        3. Si no encuentras ninguna ciudad clara, no devuelvas nada
        
        Responde ÚNICAMENTE con el nombre de la ciudad, sin ninguna explicación ni texto adicional.
        Si no encuentras ninguna ciudad, responde con la palabra "NINGUNA".
        """
        
        # Generar respuesta
        response = model.generate_content(prompt)
        
        # Obtener el texto de la respuesta y limpiarlo
        ciudad = response.text.strip()
        
        # Verificar si se encontró alguna ciudad
        if ciudad and ciudad.upper() != "NINGUNA":
            return ciudad
        
        return None
    except Exception as e:
        print(f"Error al analizar ciudad con Gemini: {e}")
        return None

# Función para completar y mejorar el nombre con Gemini
def completar_nombre_con_gemini(nombre, texto_completo):
    try:
        if not GEMINI_API_KEY or not nombre:
            return nombre
        
        # Crear modelo de Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Crear prompt para Gemini
        prompt = f"""
        Analiza el siguiente nombre que se ha extraído de un código QR: "{nombre}"
        
        Y el contenido completo del QR: "{texto_completo}"
        
        Tu tarea es:
        1. Verificar si el nombre está completo o si parece truncado o mal formateado
        2. Si está incompleto, intenta completarlo basándote en el contexto del QR
        3. Corregir cualquier error tipográfico o de formato en el nombre
        4. Mantener el nombre en MAYÚSCULAS si ya estaba en mayúsculas
        
        Responde ÚNICAMENTE con el nombre completo y corregido, sin ninguna explicación ni texto adicional.
        Si no puedes mejorar el nombre, devuelve exactamente el mismo nombre que se te proporcionó.
        """
        
        # Generar respuesta
        response = model.generate_content(prompt)
        
        # Obtener el texto de la respuesta y limpiarlo
        nombre_mejorado = response.text.strip()
        
        # Si el nombre original estaba en mayúsculas, mantenerlo así
        if nombre.isupper() and not nombre_mejorado.isupper():
            nombre_mejorado = nombre_mejorado.upper()
        
        return nombre_mejorado
    except Exception as e:
        print(f"Error al completar nombre con Gemini: {e}")
        return nombre  # En caso de error, devolver el nombre original

# Función para identificar el tipo de contenido del QR
def identificar_tipo_contenido(texto):
    # Verificar si es una URL
    url_pattern = r'^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$'
    if re.match(url_pattern, texto):
        try:
            parsed_url = urllib.parse.urlparse(texto)
            dominio = parsed_url.netloc
            return f"URL: {dominio}"
        except:
            return "URL"
    
    # Verificar si es un correo electrónico
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, texto):
        return "Correo electrónico"
    
    # Verificar si es un número de teléfono
    phone_pattern = r'^\+?[\d\s-]{7,15}$'
    if re.match(phone_pattern, texto):
        return "Número de teléfono"
    
    # Verificar si es un Wi-Fi
    if texto.startswith("WIFI:"):
        return "Configuración de Wi-Fi"
    
    # Verificar si es un contacto
    if texto.startswith("BEGIN:VCARD") or texto.startswith("MECARD:"):
        return "Información de contacto"
    
    # Verificar si es un evento de calendario
    if texto.startswith("BEGIN:VEVENT"):
        return "Evento de calendario"
    
    # Si es texto corto
    if len(texto) < 50:
        return "Texto corto"
    
    # Si es texto largo
    return "Texto largo"

# Manejador para el comando /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Verificar si el mensaje es antiguo
    if message.date < tiempo_inicio_bot:
        return
    bot.reply_to(message, "¡Hola! Soy un bot lector de códigos QR. Envíame una imagen con un código QR para leerla.")

# Manejador para el comando /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    # Verificar si el mensaje es antiguo
    if message.date < tiempo_inicio_bot:
        return
    help_text = """
    Comandos disponibles:
    /start - Iniciar el bot
    /help - Mostrar esta ayuda
    
    Funcionalidades:
    - Envía una imagen con un código QR y te mostraré su contenido.
    - El bot utiliza la biblioteca pyzbar para escanear códigos QR.
    - Puede extraer y completar nombres de personas usando IA de Google Gemini.
    - El contenido completo del QR se registra en los logs del servidor.
    """
    bot.reply_to(message, help_text)

# Manejador para imágenes
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Verificar si el mensaje es antiguo
    if message.date < tiempo_inicio_bot:
        return
    try:
        # Obtener el archivo de la foto (la más grande disponible)
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        
        # Informar al usuario que estamos procesando la imagen
        processing_msg = bot.reply_to(message, "Procesando código QR...")
        
        # Intentar decodificar el QR
        qr_data = decodificar_qr(file_bytes)
        
        if qr_data:
            # Registrar el contenido completo en los logs
            print(f"Contenido del QR: {qr_data}")
            
            # Inicializar variables
            nombre = extraer_nombre(qr_data)
            direccion = extraer_direccion(qr_data)
            ciudad = extraer_ciudad(qr_data)
            celular = extraer_celular(qr_data)
            nombre_completo = nombre
            
            # Análisis con IA sin editar mensajes intermedios
            if not ciudad and GEMINI_API_KEY:
                try:
                    ciudad = analizar_ciudad_con_gemini(qr_data)
                except Exception as e:
                    print(f"Error al analizar ciudad con Gemini: {e}")
            
            # Completar nombre con IA sin editar mensajes intermedios
            if nombre and GEMINI_API_KEY:
                try:
                    nombre_completo = completar_nombre_con_gemini(nombre, qr_data)
                except Exception as e:
                    print(f"Error al completar nombre con Gemini: {e}")
                    nombre_completo = nombre
            
            # Preparar respuesta
            respuesta_partes = []
            
            # Título con emojis
            respuesta_partes.append("🤖✨ *La IA Nequi Alpha ha detectado los siguientes datos en ese QR:* ✨🤖")
            respuesta_partes.append("")
            
            # Añadir información encontrada
            if nombre_completo:
                respuesta_partes.append(f"✅ Nombre detectado: {nombre_completo}")
                respuesta_partes.append("")
            
            if direccion:
                respuesta_partes.append(f"💠 Dirección detectada: {direccion}")
                respuesta_partes.append("")
            
            if ciudad:
                respuesta_partes.append(f"🏙️ Ciudad: {ciudad}")
                respuesta_partes.append("")
            
            if celular:
                respuesta_partes.append(f"📱 Celular: {celular}")
                respuesta_partes.append("")
            
            # Si no encontramos ninguna información relevante
            if not nombre_completo and not direccion and not ciudad and not celular:
                tipo_contenido = identificar_tipo_contenido(qr_data)
                respuesta_partes.append(f"ℹ️ Tipo de contenido: {tipo_contenido}")
                respuesta_partes.append("")
            
            # Eliminar la última línea en blanco si existe
            if respuesta_partes and respuesta_partes[-1] == "":
                respuesta_partes.pop()
            
            # Unir todas las partes de la respuesta
            respuesta = "\n".join(respuesta_partes)
            
            # Eliminar el mensaje de procesamiento y enviar uno nuevo
            try:
                bot.delete_message(message.chat.id, processing_msg.message_id)
                bot.send_message(message.chat.id, respuesta, parse_mode="Markdown")
            except Exception as e:
                print(f"Error al enviar respuesta final: {e}")
                # Si falla la eliminación, intentar editar el mensaje existente
                try:
                    bot.edit_message_text(respuesta, message.chat.id, processing_msg.message_id, parse_mode="Markdown")
                except Exception as inner_e:
                    print(f"Error al editar mensaje: {inner_e}")
        else:
            # No responder si no se detecta un QR
            # Eliminar el mensaje de procesamiento
            bot.delete_message(message.chat.id, processing_msg.message_id)
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        # Intentar notificar al usuario sobre el error
        try:
            # Si hay un mensaje de procesamiento, intentar eliminarlo y enviar uno nuevo
            if 'processing_msg' in locals() and processing_msg:
                try:
                    bot.delete_message(message.chat.id, processing_msg.message_id)
                except:
                    pass
                bot.send_message(
                    message.chat.id,
                    "❌ Error al procesar la imagen. Por favor, asegúrate de que la imagen contiene un código QR válido y vuelve a intentarlo."
                )
            else:
                # Si no hay mensaje de procesamiento, enviar uno nuevo
                bot.reply_to(
                    message,
                    "❌ Error al procesar la imagen. Por favor, asegúrate de que la imagen contiene un código QR válido y vuelve a intentarlo."
                )
        except Exception as inner_e:
            print(f"Error al notificar al usuario: {inner_e}")

# Añadir soporte para webhook
@bot.message_handler(func=lambda message: True, content_types=['text'])
def webhook_handler(message):
    # Verificar si el mensaje es antiguo
    if message.date < tiempo_inicio_bot:
        return
    # No responder a mensajes de texto
    pass

# Solo iniciar el polling si se ejecuta directamente
if __name__ == "__main__":
    print("Bot iniciado...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 