import os

def list_files(startpath, exclude_dirs=None, exclude_files=None, max_level=3):
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()

    for root, dirs, files in os.walk(startpath):
        # Calcular el nivel actual
        level = root.replace(startpath, '').count(os.sep)

        # Si el nivel supera el máximo, detener la recursión
        if level > max_level:
            continue

        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # Imprimir el nombre del directorio actual
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")

        # Imprimir archivos en el directorio actual
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not any(f.endswith(ext) for ext in exclude_files):
                print(f"{subindent}{f}")

# Configuración
startpath = '.'  # Directorio actual
exclude_dirs = {'__pycache__', '.git', '.pytest_cache'}  # Excluir estos directorios
exclude_files = {'.pyc', '.pyo'}  # Excluir estos archivos
max_level = 3  # Límite de niveles

# Listar estructura
list_files(startpath, exclude_dirs, exclude_files, max_level)