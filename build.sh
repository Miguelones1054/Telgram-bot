#!/bin/bash
# Script de build personalizado para Render

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del sistema (si están disponibles)
# Estas son las dependencias que qreader necesita
apt-get update -qq && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    python3-wheel \
    || echo "Algunas dependencias del sistema no están disponibles, continuando..."

# Instalar dependencias de Python
pip install -r requirements.txt

echo "Build completado" 