#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para tareas administrativas (manage.py).
Permite arrancar el servidor de desarrollo, ejecutar migraciones, pruebas unitarias
y crear superusuarios desde la consola.
"""

import os
import sys

def main():
    """
    Función principal que arranca las tareas administrativas de Django.
    """
    # Establecer la configuración de Django por defecto para el entorno
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_reportes.settings')
    try:
        # Importar y ejecutar la línea de comandos de Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste "
            "activar el entorno virtual (venv)?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
