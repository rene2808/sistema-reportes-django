import datetime
from django.core.cache import cache
from django.utils import timezone

class ActiveUserMiddleware:
    """
    Middleware que registra la última actividad de cada usuario autenticado
    para determinar si se encuentra en línea.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Almacena en la caché la fecha y hora actual para el ID del usuario
            # con un tiempo de expiración de 10 minutos (600 segundos)
            cache.set(f'seen_user_{request.user.id}', timezone.now(), 600)
        
        response = self.get_response(request)
        return response
