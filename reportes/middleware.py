import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ActiveUserMiddleware:
    """
    Middleware que registra la última actividad de cada usuario autenticado
    para determinar si se encuentra en línea de forma segura y evita
    el almacenamiento en caché de páginas privadas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Almacena en la caché un valor booleano simple (evita problemas de serialización)
                # con un tiempo de expiración de 10 minutos (600 segundos)
                cache.set(f'seen_user_{request.user.id}', True, 600)
            except Exception as e:
                # Registra el error pero permite que la petición continúe sin caer en error 500
                logger.error(f"Error al actualizar la caché de actividad del usuario: {e}")
        
        response = self.get_response(request)

        # Si el usuario está autenticado, agregamos cabeceras HTTP para impedir que el navegador 
        # almacene en caché las páginas privadas. Esto evita que, al cerrar la sesión 
        # y presionar el botón "Atrás/Volver", se muestre información sensible cargada en caché.
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
