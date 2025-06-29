# Escáner de Códigos QR con Extracción de Datos

Esta aplicación web permite escanear códigos QR y extraer información relevante como nombres, direcciones, ciudades y números de teléfono.

## Funcionalidades

- Lectura de códigos QR desde imágenes subidas
- Captura de códigos QR usando la cámara del dispositivo
- Extracción de nombres usando expresiones regulares
- Extracción de direcciones y números de teléfono
- Mejora de la detección usando la API de Google Gemini (opcional)
- Interfaz web moderna y responsive

## Tecnologías utilizadas

- Python con Flask para el backend
- HTML, CSS y JavaScript para el frontend
- Bootstrap para el diseño responsive
- pyzbar y OpenCV para la lectura de códigos QR
- Google Gemini API para mejorar la detección (opcional)

## Requisitos

- Python 3.9 o superior
- Bibliotecas especificadas en requirements.txt
- En sistemas Linux, puede necesitar instalar libzbar: `apt-get install libzbar0 zbar-tools`

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/escaner-qr.git
cd escaner-qr
```

2. Crear un entorno virtual e instalar dependencias:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno (opcional):
Crea un archivo `.env` en el directorio raíz con:
```
GEMINI_API_KEY=tu_api_key_de_google_gemini
```

## Uso

1. Iniciar la aplicación:
```
python app.py
```

2. Abrir en el navegador:
```
http://localhost:5000
```

3. Usar la aplicación:
   - Subir una imagen con un código QR, o
   - Usar la cámara para escanear un código QR en tiempo real

## Despliegue en Render

1. Crea una cuenta en [Render](https://render.com/)
2. Crea un nuevo Web Service
3. Conecta tu repositorio de GitHub
4. Configura:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Variables de entorno:
     - `GEMINI_API_KEY`: Tu API key de Google Gemini (opcional)

## API

La aplicación ofrece un endpoint API para integración con otros sistemas:

- `POST /api/scan`: Envía una imagen para escanear un código QR
  - Parámetro: `file` (archivo de imagen)
  - Respuesta: JSON con la información extraída

## Licencia

Este proyecto está bajo la Licencia MIT.