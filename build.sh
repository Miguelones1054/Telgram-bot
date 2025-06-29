#!/usr/bin/env bash
# Script para instalar dependencias necesarias en Render

# Instalar zbar
apt-get update
apt-get install -y libzbar0 libzbar-dev

# Instalar dependencias de Python
pip install -r requirements.txt 