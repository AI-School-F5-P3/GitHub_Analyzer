# tests/conftest.py
import sys
import os
import pytest
from pathlib import Path
from django.conf import settings

# No es necesario configurar PYTHONPATH aquí si ya lo hiciste en el conftest.py raíz
# pero si lo mantienes, asegúrate de que la ruta sea correcta

print("Configurando bases de datos para pruebas...")

@pytest.fixture(scope='session')
def django_db_setup():
    """Configura la base de datos de prueba para Django."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }