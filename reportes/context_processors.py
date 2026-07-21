"""
Módulo de Procesadores de Contexto para la aplicación de Reportes.
Permite inyectar variables globales (como el contador de notificaciones sin leer)
en todas las plantillas HTML renderizadas en el sistema.
"""

from .models import Notificacion

def notificaciones_context(request):
    """
    Inyecta el contador de notificaciones no leídas en el contexto de todas las plantillas.
    Esto permite mostrar la burbuja de notificación en la barra de navegación.
    """
    if request.user.is_authenticated:
        # Contar notificaciones que pertenecen al usuario y no han sido marcadas como leídas
        unread_count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return {
            'notificaciones_sin_leer_count': unread_count
        }
    # Si el usuario no está autenticado, el contador es 0
    return {
        'notificaciones_sin_leer_count': 0
    }
