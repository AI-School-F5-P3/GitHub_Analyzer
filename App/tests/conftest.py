# tests/conftest.py
import sys
import os
from pathlib import Path

print("Configurando PYTHONPATH y Django...")

# Añadir la ruta del proyecto al PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Sube 3 niveles desde tests/
sys.path.append(str(BASE_DIR))

import pytest
from django.conf import settings
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup():
    """Configura la base de datos de prueba para Django."""
    print("Configurando la base de datos de Django...")
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    call_command('migrate')