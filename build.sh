#!/usr/bin/env bash
# Termina el script en caso de error
set -o errexit  

# Instala las dependencias de Python
pip install -r requirements.txt

# Realiza migraciones de base de datos y colecta archivos estáticos
python manage.py collectstatic --no-input
python manage.py migrate