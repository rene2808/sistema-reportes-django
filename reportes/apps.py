"""
Módulo de Configuración de la Aplicación para reportes.
Define los ajustes iniciales para registrar la aplicación de Reportes en Django.
"""

from django.apps import AppConfig

class ReportesConfig(AppConfig):
    """
    Clase de configuración de la aplicación 'reportes'.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reportes'
