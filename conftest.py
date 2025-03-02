import os
import sys
import django
from pathlib import Path

# Obtener la ruta absoluta del directorio del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Asegurar que 'App/' esté en el path para que se reconozca `repo_analyzer`
sys.path.insert(0, str(BASE_DIR / "App"))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "App.repo_analyzer.settings")
django.setup()

print(f"PYTHONPATH configurado: {sys.path}")
print(f"Django configurado con settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")