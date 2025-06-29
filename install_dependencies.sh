#!/bin/bash
set -e

echo "=== INICIANDO INSTALACIÓN DE DEPENDENCIAS ==="

# Función para mostrar información del sistema
show_system_info() {
    echo "=== INFORMACIÓN DEL SISTEMA ==="
    uname -a
    cat /etc/os-release || echo "No se pudo obtener información del sistema operativo"
    echo "Python: $(python --version)"
    echo "Pip: $(pip --version)"
    echo "==========================="
}

# Mostrar información del sistema
show_system_info

echo "=== INSTALANDO DEPENDENCIAS DEL SISTEMA ==="

# Intentar con sudo si está disponible
if command -v sudo &> /dev/null; then
    echo "Usando sudo para instalar dependencias..."
    sudo apt-get update -y || echo "Error en apt-get update"
    sudo apt-get install -y libzbar0 zbar-tools python3-dev build-essential || echo "Error al instalar paquetes"
else
    # Intentar sin sudo
    echo "Intentando instalar sin sudo..."
    apt-get update -y || echo "Error en apt-get update"
    apt-get install -y libzbar0 zbar-tools python3-dev build-essential || echo "Error al instalar paquetes"
fi

echo "=== VERIFICANDO INSTALACIÓN DE LIBZBAR ==="
if [ -f "/usr/lib/x86_64-linux-gnu/libzbar.so.0" ]; then
    echo "libzbar encontrado en /usr/lib/x86_64-linux-gnu/libzbar.so.0"
elif [ -f "/usr/lib/libzbar.so.0" ]; then
    echo "libzbar encontrado en /usr/lib/libzbar.so.0"
else
    echo "¡ADVERTENCIA! No se encontró libzbar.so.0"
    echo "Buscando libzbar en el sistema..."
    find /usr -name "libzbar*" 2>/dev/null || echo "No se encontraron archivos libzbar"
fi

echo "=== INSTALANDO DEPENDENCIAS DE PYTHON ==="
pip install --upgrade pip
pip install wheel setuptools

# Instalar dependencias básicas primero
echo "Instalando dependencias básicas..."
pip install numpy==1.24.3 Pillow==9.5.0 requests==2.31.0 python-dotenv==1.0.0

# Intentar instalar pyzbar directamente
echo "Intentando instalar pyzbar..."
pip install pyzbar==0.1.9 || echo "Error al instalar pyzbar, continuando..."

# Instalar OpenCV como alternativa
echo "Instalando OpenCV..."
pip install opencv-python-headless==4.8.0.74 || echo "Error al instalar OpenCV, continuando..."

# Instalar el resto de dependencias
echo "Instalando el resto de dependencias..."
pip install pyTelegramBotAPI==4.14.0 google-generativeai==0.3.2

# Instalar el proyecto actual
echo "Instalando el proyecto..."
pip install -e . || echo "Error al instalar el proyecto, continuando..."

echo "=== VERIFICANDO INSTALACIÓN DE PAQUETES PYTHON ==="
pip list | grep -E 'pyzbar|opencv|Pillow|numpy|pyTelegramBotAPI'

echo "=== INSTALACIÓN COMPLETADA ===" 