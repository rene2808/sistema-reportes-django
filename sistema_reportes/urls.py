"""
Configuración de URLs principales para el proyecto 'sistema_reportes'.
Redirecciona las rutas de la raíz y de administración (/admin/) hacia sus
respectivas aplicaciones y enrutadores.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta por defecto para el panel de administración general de Django
    path('admin/', admin.site.urls),

    # Incluir las URLs de la aplicación local 'reportes' para enrutamiento
    path('', include('reportes.urls')),
]

# Servir archivos multimedia (media) subidos por los usuarios en entorno de desarrollo local (DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Añadir al final del archivo:
if settings.DEBUG or not settings.DEBUG:  # Para asegurar que sirva media en Render sin S3/Cloudinary
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)