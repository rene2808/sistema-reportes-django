import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class ActiveUserMiddleware:
    """
    Middleware que registra la última actividad de cada usuario autenticado
    en la base de datos para determinar si se encuentra en línea
    de forma segura e impide el almacenamiento en caché de páginas privadas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Verificar si el usuario está bloqueado temporal o permanentemente
                perfil = request.user.perfilusuario
                if not request.user.is_active or (perfil.bloqueado_hasta and perfil.bloqueado_hasta > timezone.now()):
                    from django.contrib.auth import logout
                    logout(request)
                else:
                    from reportes.models import PerfilUsuario
                    # Actualiza de forma directa y rápida el campo ultimo_acceso en la base de datos
                    PerfilUsuario.objects.filter(usuario=request.user).update(ultimo_acceso=timezone.now())
            except Exception as e:
                # Registra el error pero permite que la petición continúe sin interrumpir al usuario
                logger.error(f"Error al actualizar la actividad del usuario en base de datos: {e}")
        
        response = self.get_response(request)

        # Si el usuario está autenticado, agregamos cabeceras HTTP para impedir que el navegador 
        # almacene en caché las páginas privadas. Esto evita que, al cerrar la sesión 
        # y presionar el botón "Atrás/Volver", se muestre información sensible cargada en caché.
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
