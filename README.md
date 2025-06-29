# QR Scanner Bot - FastAPI

Bot de Telegram para escanear códigos QR y procesar información usando FastAPI.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs
- **Escaneo de QR**: Múltiples bibliotecas de soporte (qreader, pyzbar, OpenCV)
- **Procesamiento de imágenes**: Análisis avanzado con Google Gemini AI
- **API REST**: Endpoints para integración con otros servicios
- **Interfaz web**: Interfaz de usuario para subir y procesar imágenes

## 📦 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en desarrollo
python app.py

# O ejecutar directamente con uvicorn
uvicorn app:app --reload --host=0.0.0.0 --port=8000
```

## 🔧 Configuración

1. Crea un archivo `.env` con tus variables de entorno:
```env
GEMINI_API_KEY=tu_api_key_de_google_gemini
```

## 📡 Endpoints

- `GET /`: Interfaz web principal
- `POST /upload`: Subir y procesar imagen con QR
- `POST /api/scan`: API para escanear QR (sin interfaz)
- `GET /health`: Verificación de salud del servicio
- `GET /docs`: Documentación automática de la API

## 🚀 Despliegue

### Heroku
```bash
git push heroku main
```

### Local
```bash
python uvicorn_config.py
```

## 📊 Ventajas de FastAPI

- ⚡ **Rendimiento**: Hasta 3x más rápido que Flask
- 🔄 **Asíncrono**: Mejor manejo de conexiones concurrentes
- 📝 **Documentación automática**: Swagger/OpenAPI incluido
- 🛡️ **Validación automática**: Type hints y Pydantic
- 🎯 **Optimizado para APIs**: Diseñado específicamente para servicios web

## 🔍 Uso

1. Abre `http://localhost:8000` en tu navegador
2. Sube una imagen con código QR
3. El sistema procesará la imagen y extraerá la información
4. Los resultados se mostrarán en la interfaz web

## 📝 Notas

- El puerto por defecto cambió de 5000 (Flask) a 8000 (FastAPI)
- La documentación automática está disponible en `/docs`
- El endpoint de salud está en `/health`
