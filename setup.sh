#!/bin/bash

# Actualizar repositorios
apt-get update

# Instalar dependencias para pyzbar
apt-get install -y libzbar0 zbar-tools

# Limpiar caché de apt para reducir el tamaño de la imagen
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "Dependencias instaladas correctamente" 