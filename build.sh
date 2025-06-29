#!/bin/bash

# Actualizar repositorios
apt-get update

# Instalar dependencias para pyzbar
apt-get install -y libzbar0 zbar-tools

# Instalar dependencias de Python
pip install -r requirements.txt

echo "Construcción completada con éxito" 