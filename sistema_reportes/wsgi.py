"""
Configuración WSGI para el proyecto 'sistema_reportes'.
Expone la interfaz de entrada para servidores web compatibles con WSGI (ej. Gunicorn, Apache mod_wsgi),
utilizada convencionalmente para desplegar la aplicación Django en producción.
"""

import os
from django.core.wsgi import get_wsgi_application

# Establecer la configuración de Django por defecto para el entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_reportes.settings')

# Inicializar y exponer la aplicación WSGI
application = get_wsgi_application()
