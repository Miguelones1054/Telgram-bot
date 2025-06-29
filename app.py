import os
import io
import base64
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from qr_scanner import procesar_imagen_qr
import uvicorn

app = FastAPI(
    title="QR Scanner API",
    description="API para escanear códigos QR y procesar información",
    version="1.0.0"
)

# Configuración
app.config = {
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16 MB máximo
    'UPLOAD_FOLDER': 'uploads'
}

# Asegurarse de que el directorio de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con interfaz web"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint para subir y procesar archivos de imagen con códigos QR
    """
    # Verificar que se envió un archivo
    if not file:
        print("[ERROR] No se envió ningún archivo")
        raise HTTPException(status_code=400, detail="No se envió ningún archivo")
    
    # Verificar que el archivo sea una imagen permitida
    if not allowed_file(file.filename):
        print(f"[ERROR] Tipo de archivo no permitido: {file.filename}")
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    try:
        # Leer el archivo como bytes
        file_bytes = await file.read()
        print(f"[INFO] Archivo recibido: {file.filename}, tamaño: {len(file_bytes)} bytes")
        
        # Guardar la imagen recibida para depuración
        tmp_path = f"/tmp/recibido_{file.filename}"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)
        print(f"[DEBUG] Imagen guardada en {tmp_path}")
        
        # Verificar el tamaño del archivo
        if len(file_bytes) > app.config['MAX_CONTENT_LENGTH']:
            print(f"[ERROR] Archivo demasiado grande: {len(file_bytes)} bytes")
            raise HTTPException(status_code=400, detail="Archivo demasiado grande")
        
        # Procesar la imagen
        resultado = procesar_imagen_qr(file_bytes)
        
        # Si hay un error, devolverlo
        if 'error' in resultado:
            print(f"[ERROR] {resultado['error']}")
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        # Convertir la imagen a base64 para mostrarla en el resultado
        encoded_image = base64.b64encode(file_bytes).decode('utf-8')
        resultado['imagen'] = encoded_image
        print(f"[SUCCESS] QR procesado correctamente para {file.filename}")
        return JSONResponse(content=resultado)
        
    except HTTPException as e:
        print(f"[HTTPException] {e.detail}")
        raise
    except Exception as e:
        print(f"[ERROR 500] Error al procesar la imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

@app.post("/api/scan")
async def api_scan(file: UploadFile = File(...)):
    """
    API endpoint para escanear códigos QR (sin interfaz web)
    """
    # Verificar que se envió un archivo
    if not file:
        print("[ERROR] No se envió ningún archivo (API)")
        raise HTTPException(status_code=400, detail="No se envió ningún archivo")
    
    # Verificar que el archivo sea una imagen permitida
    if not allowed_file(file.filename):
        print(f"[ERROR] Tipo de archivo no permitido (API): {file.filename}")
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    try:
        # Leer el archivo como bytes
        file_bytes = await file.read()
        print(f"[INFO] Archivo recibido (API): {file.filename}, tamaño: {len(file_bytes)} bytes")
        
        # Guardar la imagen recibida para depuración
        tmp_path = f"/tmp/recibido_{file.filename}"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)
        print(f"[DEBUG] Imagen guardada en {tmp_path} (API)")
        
        # Verificar el tamaño del archivo
        if len(file_bytes) > app.config['MAX_CONTENT_LENGTH']:
            print(f"[ERROR] Archivo demasiado grande (API): {len(file_bytes)} bytes")
            raise HTTPException(status_code=400, detail="Archivo demasiado grande")
        
        # Procesar la imagen
        resultado = procesar_imagen_qr(file_bytes)
        
        # Si hay un error, devolverlo
        if 'error' in resultado:
            print(f"[ERROR] {resultado['error']} (API)")
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        print(f"[SUCCESS] QR procesado correctamente para {file.filename} (API)")
        return JSONResponse(content=resultado)
        
    except HTTPException as e:
        print(f"[HTTPException] {e.detail} (API)")
        raise
    except Exception as e:
        print(f"[ERROR 500] Error al procesar la imagen (API): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {"status": "healthy", "service": "QR Scanner API"}

if __name__ == "__main__":
    # Render usa puerto 10000 por defecto, pero también acepta la variable PORT
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Desactivar reload en producción
        log_level="info"
    ) 