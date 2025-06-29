import os
import io
import base64
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from qr_scanner import procesar_imagen_qr

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB máximo
app.config['UPLOAD_FOLDER'] = 'uploads'

# Asegurarse de que el directorio de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensiones de archivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificar si se envió un archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    # Si el usuario no selecciona un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Verificar que el archivo sea una imagen permitida
    if file and allowed_file(file.filename):
        # Leer el archivo como bytes
        file_bytes = file.read()
        
        try:
            # Procesar la imagen
            resultado = procesar_imagen_qr(file_bytes)
            
            # Si hay un error, devolverlo
            if 'error' in resultado:
                return jsonify(resultado), 400
            
            # Convertir la imagen a base64 para mostrarla en el resultado
            encoded_image = base64.b64encode(file_bytes).decode('utf-8')
            resultado['imagen'] = encoded_image
            
            return jsonify(resultado)
        except Exception as e:
            return jsonify({'error': f'Error al procesar la imagen: {str(e)}'}), 500
    
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

@app.route('/api/scan', methods=['POST'])
def api_scan():
    # Verificar si se envió un archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    # Si el usuario no selecciona un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Verificar que el archivo sea una imagen permitida
    if file and allowed_file(file.filename):
        # Leer el archivo como bytes
        file_bytes = file.read()
        
        try:
            # Procesar la imagen
            resultado = procesar_imagen_qr(file_bytes)
            return jsonify(resultado)
        except Exception as e:
            return jsonify({'error': f'Error al procesar la imagen: {str(e)}'}), 500
    
    return jsonify({'error': 'Tipo de archivo no permitido'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 