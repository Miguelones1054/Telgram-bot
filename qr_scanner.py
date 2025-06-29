import os
import sys
import re
import urllib.parse
from io import BytesIO
import numpy as np
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno
try:
    load_dotenv()
except ImportError:
    print("Módulo python-dotenv no encontrado.")

# Configurar API de Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Verificar API key de Gemini
if GEMINI_API_KEY:
    # Configurar Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    print("API de Google Gemini configurada correctamente")
else:
    print("ADVERTENCIA: No se encontró la API key de Google Gemini en las variables de entorno.")
    print("El análisis avanzado no estará disponible.")

# Intentar instalar zbar si estamos en Linux
try:
    import platform
    if platform.system() == "Linux":
        print("Detectado sistema Linux, intentando instalar zbar...")
        import subprocess
        try:
            subprocess.check_call(["apt-get", "update"])
            subprocess.check_call(["apt-get", "install", "-y", "libzbar0", "libzbar-dev"])
            print("Instalación de zbar completada")
        except Exception as e:
            print(f"Error al instalar zbar: {e}")
except Exception as e:
    print(f"Error al verificar el sistema: {e}")

# Importar bibliotecas para QR
qreader_available = False
pyzbar_available = False
cv2_available = False

# Intentar importar múltiples bibliotecas para lectura de QR
print("Intentando cargar bibliotecas para lectura de QR...")

# 1. Intentar con qreader (primera opción)
try:
    import qreader
    qreader_available = True
    print("Biblioteca qreader cargada correctamente")
except ImportError as e:
    print(f"Error al cargar qreader: {e}")
    
    # Intentar instalar qreader automáticamente
    try:
        import subprocess
        print("Intentando instalar qreader...")
        subprocess.check_call(["pip", "install", "qreader"])
        import qreader
        qreader_available = True
        print("Biblioteca qreader instalada y cargada correctamente")
    except Exception as e:
        print(f"Error al instalar qreader: {e}")

# 2. Intentar con pyzbar (segunda opción)
if not qreader_available:
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

# 3. Intentar con OpenCV como última alternativa
if not qreader_available and not pyzbar_available:
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

if not qreader_available and not pyzbar_available and not cv2_available:
    print("Error crítico: No se encontraron bibliotecas para leer QR.")
    print("Este programa requiere alguna de estas bibliotecas: qreader, pyzbar o OpenCV")
    print("En sistemas Linux, ejecuta: apt-get install libzbar0 zbar-tools")
    sys.exit(1)
else:
    print("Al menos una biblioteca para lectura de QR está disponible")

# Función para normalizar el resultado de la decodificación QR
def normalizar_resultado_qr(resultado):
    """
    Normaliza el resultado de la decodificación QR para asegurar que siempre sea una cadena.
    
    Args:
        resultado: El resultado de la decodificación QR (puede ser cadena, tupla, etc.)
        
    Returns:
        str: Una cadena normalizada
    """
    if resultado is None:
        return None
    
    # Si es una tupla o lista, tomar el primer elemento
    if isinstance(resultado, (tuple, list)):
        if len(resultado) > 0:
            # Recursivamente normalizar el primer elemento
            return normalizar_resultado_qr(resultado[0])
        else:
            return None
    
    # Si ya es una cadena, devolverla
    if isinstance(resultado, str):
        return resultado
    
    # Intentar convertir a cadena
    try:
        return str(resultado)
    except Exception as e:
        print(f"Error al normalizar resultado QR: {e}")
        return None

# Función para decodificar QR usando las bibliotecas disponibles
def decodificar_qr(imagen_bytes):
    try:
        # Convertir bytes a imagen
        img = Image.open(BytesIO(imagen_bytes))
        
        # 1. Intentar con qreader si está disponible (mejor rendimiento)
        if qreader_available:
            # Convertir PIL a numpy array
            img_array = np.array(img)
            
            # Verificar si la imagen tiene 4 canales (RGBA) y convertirla a RGB
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                # Convertir RGBA a RGB
                img_rgb = Image.fromarray(img_array).convert('RGB')
                img_array = np.array(img_rgb)
                print("Imagen convertida de RGBA a RGB")
            
            # Crear detector QR
            detector = qreader.QReader()
            
            try:
                # Decodificar QR
                decoded_result = detector.detect_and_decode(image=img_array, return_detections=False)
                
                # Normalizar el resultado (convertir tupla a cadena si es necesario)
                decoded_text = normalizar_resultado_qr(decoded_result)
                
                if decoded_text:
                    print(f"Contenido del QR (qreader): {decoded_result}")
                    print(f"Contenido normalizado: {decoded_text}")
                    return decoded_text
            except Exception as e:
                print(f"Error con qreader: {e}")
                # Si falla qreader, continuamos con otros métodos
            
            # Si no se encontró ningún QR, intentar con una imagen procesada
            try:
                # Asegurarse de que la imagen es RGB para evitar errores
                if len(img_array.shape) == 3 and img_array.shape[2] == 3 and cv2_available:
                    img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    _, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
                    
                    # Intentar de nuevo con la imagen procesada
                    decoded_result = detector.detect_and_decode(image=img_thresh, return_detections=False)
                    
                    # Normalizar el resultado
                    decoded_text = normalizar_resultado_qr(decoded_result)
                    
                    if decoded_text:
                        print(f"Contenido del QR (qreader - imagen procesada): {decoded_result}")
                        print(f"Contenido normalizado: {decoded_text}")
                        return decoded_text
            except Exception as e:
                print(f"Error con qreader (imagen procesada): {e}")
                # Si falla, continuamos con otros métodos
        
        # 2. Intentar con pyzbar si está disponible o si qreader falló
        if pyzbar_available:
            try:
                decoded_objects = pyzbar_decode(img)
                for obj in decoded_objects:
                    decoded_text = obj.data.decode('utf-8')
                    print(f"Contenido del QR (pyzbar): {decoded_text}")
                    return decoded_text
            except Exception as e:
                print(f"Error con pyzbar: {e}")
            
            # Si no se encontró ningún QR, intentar con una imagen procesada
            try:
                img_gray = img.convert('L')
                img_contrast = Image.eval(img_gray, lambda x: 0 if x < 128 else 255)
                
                decoded_objects = pyzbar_decode(img_contrast)
                for obj in decoded_objects:
                    decoded_text = obj.data.decode('utf-8')
                    print(f"Contenido del QR (pyzbar - imagen procesada): {decoded_text}")
                    return decoded_text
            except Exception as e:
                print(f"Error con pyzbar (imagen procesada): {e}")
        
        # 3. Intentar con OpenCV si está disponible o si los anteriores fallaron
        if cv2_available:
            try:
                # Convertir PIL a OpenCV
                img_array = np.array(img)
                
                # Si la imagen es RGBA, convertirla a RGB
                if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                else:
                    img_rgb = img_array
                
                img_cv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                
                # Crear detector QR
                qr_detector = cv2.QRCodeDetector()
                data, bbox, _ = qr_detector.detectAndDecode(img_cv)
                
                if data:
                    print(f"Contenido del QR (OpenCV): {data}")
                    return data
            except Exception as e:
                print(f"Error con OpenCV: {e}")
            
            # Intentar con imagen procesada
            try:
                img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                _, img_thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
                data, bbox, _ = qr_detector.detectAndDecode(img_thresh)
                
                if data:
                    print(f"Contenido del QR (OpenCV - imagen procesada): {data}")
                    return data
            except Exception as e:
                print(f"Error con OpenCV (imagen procesada): {e}")
        
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
    
    # Buscar "BOGOTA" en el contenido QR
    if "BOGOTA" in texto:
        return "BOGOTA"
    
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
    
    # Verificar si parece ser un código QR de pago o factura
    if "SUPERMERCADO" in texto or "RBM" in texto:
        return "Factura o comprobante de pago"
    
    # Si es texto corto
    if len(texto) < 50:
        return "Texto corto"
    
    # Si es texto largo
    return "Texto largo"

# Función principal para procesar una imagen QR
def procesar_imagen_qr(imagen_bytes):
    """
    Procesa una imagen con un código QR y extrae información relevante.
    
    Args:
        imagen_bytes: Bytes de la imagen a procesar
        
    Returns:
        dict: Diccionario con la información extraída
    """
    # Intentar decodificar el QR
    qr_data = decodificar_qr(imagen_bytes)
    
    if not qr_data:
        return {"error": "No se detectó ningún código QR en la imagen"}
    
    # Registrar el contenido completo
    print(f"Contenido del QR: {qr_data}")
    
    # Inicializar variables
    nombre = extraer_nombre(qr_data)
    direccion = extraer_direccion(qr_data)
    ciudad = extraer_ciudad(qr_data)
    celular = extraer_celular(qr_data)
    nombre_completo = nombre
    
    # Buscar nombre de establecimiento en el QR
    if not nombre and "SUPERMERCADO EL IMPERI" in qr_data:
        nombre_completo = "SUPERMERCADO EL IMPERIO"
    
    # Análisis con IA
    if not ciudad and GEMINI_API_KEY:
        try:
            ciudad = analizar_ciudad_con_gemini(qr_data)
        except Exception as e:
            print(f"Error al analizar ciudad con Gemini: {e}")
    
    # Completar nombre con IA
    if nombre and GEMINI_API_KEY:
        try:
            nombre_completo = completar_nombre_con_gemini(nombre, qr_data)
        except Exception as e:
            print(f"Error al completar nombre con Gemini: {e}")
            nombre_completo = nombre
    
    # Preparar respuesta
    resultado = {
        "contenido_qr": qr_data,
        "nombre": nombre_completo,
        "direccion": direccion,
        "ciudad": ciudad,
        "celular": celular,
        "tipo_contenido": None
    }
    
    # Si no encontramos ninguna información relevante
    if not nombre_completo and not direccion and not ciudad and not celular:
        tipo_contenido = identificar_tipo_contenido(qr_data)
        resultado["tipo_contenido"] = tipo_contenido
    
    return resultado

# Función para pruebas
if __name__ == "__main__":
    # Ejemplo de uso
    print("Este módulo proporciona funciones para escanear códigos QR.")
    print("Importa este módulo y usa la función procesar_imagen_qr() para procesar imágenes con códigos QR.") 