"""
Configuración ASGI para el proyecto 'sistema_reportes'.
Expone la interfaz de entrada para servidores compatibles con ASGI (ej. Daphne, Uvicorn),
utilizada en entornos de producción para conexiones asíncronas y WebSockets.
"""

import os
from django.core.asgi import get_asgi_application

# Establecer la configuración de Django por defecto para el entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_reportes.settings')

# Inicializar y exponer la aplicación ASGI
application = get_asgi_application()
