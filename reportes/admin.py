"""
Módulo de Administración de Django para la aplicación de Reportes.
Permite registrar y configurar cómo se muestran y gestionan los modelos
del sistema en el sitio de administración oficial de Django (/admin/).
"""

# Importación de la librería de administración nativa de Django
from django.contrib import admin

# Importación de los modelos definidos en models.py para su registro en el panel admin
from .models import (
    Categoria,
    TipoProblema,
    EstadoReporte,
    Prioridad,
    Rol,
    PerfilUsuario,
    Reporte,
    Evidencia,
    HistorialCambio,
    Notificacion,
    HistorialReporte,
    Resena,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Categoria.
    """
    # Columnas que se mostrarán en la tabla de listado de categorías en el panel
    list_display = ('id', 'nombre', 'codigo')
    
    # Campos sobre los cuales se puede realizar una búsqueda de texto
    search_fields = ('nombre', 'codigo')


# [LEGACY / NO UTILIZADO]
@admin.register(TipoProblema)
class TipoProblemaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo TipoProblema (Catálogo Legacy).
    """
    # Columnas mostradas en el listado del panel de administración
    list_display = ('id', 'categoria', 'nombre')
    
    # Filtros laterales disponibles para agrupar por categoría
    list_filter = ('categoria',)
    
    # Campos de búsqueda que incluyen búsqueda relacional en Categoria
    search_fields = ('nombre', 'categoria__nombre')


# [LEGACY / NO UTILIZADO]
@admin.register(EstadoReporte)
class EstadoReporteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo EstadoReporte (Catálogo Legacy).
    """
    # Columnas mostradas en el listado de estados de reporte
    list_display = ('id', 'nombre', 'orden')
    
    # Criterio de ordenamiento por defecto para las filas de estados
    ordering = ('orden',)
    
    # Campos que admiten búsqueda de texto en el panel
    search_fields = ('nombre',)


# [LEGACY / NO UTILIZADO]
@admin.register(Prioridad)
class PrioridadAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Prioridad (Catálogo Legacy).
    """
    # Columnas mostradas en la tabla del panel admin
    list_display = ('id', 'nombre', 'nivel')
    
    # Ordenación por el campo nivel de prioridad (ascendente)
    ordering = ('nivel',)
    
    # Campos con soporte para búsquedas de texto
    search_fields = ('nombre',)


# [LEGACY / NO UTILIZADO]
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Rol (Catálogo Legacy).
    """
    # Columnas a visualizar en el listado de roles
    list_display = ('id', 'nombre')
    
    # Criterio de búsqueda en el panel admin
    search_fields = ('nombre',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo PerfilUsuario.
    """
    # Campos expuestos para visualizar en el listado del perfil de usuario
    list_display = ('usuario', 'rol', 'telefono')
    
    # Filtro lateral para segmentar los perfiles de usuario por rol
    list_filter = ('rol',)
    
    # Campos de búsqueda, incluyendo campos del modelo de Usuario heredado
    search_fields = ('usuario__username', 'usuario__email', 'telefono')


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo de Reporte (Bitácora principal de incidentes).
    """
    # Columnas visibles del reporte en la tabla principal de administración
    list_display = (
        'folio',
        'usuario',
        'categoria',
        'titulo',
        'colonia',
        'prioridad',
        'estado',
        'mostrar_en_galeria',
        'fecha_reporte',
    )

    # Filtros rápidos ubicados a la derecha para clasificar incidencias
    list_filter = (
        'categoria',
        'prioridad',
        'estado',
        'mostrar_en_galeria',
        'fecha_reporte',
    )

    # Permite buscar coincidencias de texto cruzando campos de usuario y categoría
    search_fields = (
        'folio',
        'usuario__username',
        'usuario__email',
        'categoria__nombre',
        'titulo',
        'descripcion',
        'colonia',
        'calle',
        'referencia',
    )

    # Campos protegidos contra modificaciones en el formulario del panel
    readonly_fields = (
        'folio',
        'fecha_reporte',
    )


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Evidencia (fotos de reparación).
    """
    # Columnas expuestas para visualizar en la tabla del panel
    list_display = (
        'id',
        'reporte',
        'descripcion',
        'fecha_subida',
    )

    # Filtro lateral por fecha de carga de la evidencia
    list_filter = (
        'fecha_subida',
    )

    # Campos de búsqueda del panel admin
    search_fields = (
        'reporte__folio',
        'descripcion',
    )


# [LEGACY / NO UTILIZADO]
@admin.register(HistorialCambio)
class HistorialCambioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo HistorialCambio (Legacy).
    """
    # Columnas mostradas en el listado de cambios
    list_display = (
        'id',
        'reporte',
        'usuario',
        'accion',
        'fecha',
    )

    # Filtros laterales rápidos por acción y fecha de cambio
    list_filter = (
        'accion',
        'fecha',
    )

    # Búsqueda detallada por folio, usuario o acción
    search_fields = (
        'reporte__folio',
        'usuario__username',
        'accion',
        'descripcion',
    )


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Notificacion.
    """
    # Columnas mostradas en el listado del panel de notificaciones
    list_display = (
        'usuario',
        'reporte',
        'titulo',
        'leida',
        'fecha',
    )

    # Filtros rápidos para ver notificaciones leídas/no leídas y por fecha
    list_filter = (
        'leida',
        'fecha',
    )

    # Soporte de búsqueda por campos relacionados y texto libre
    search_fields = (
        'usuario__username',
        'titulo',
        'mensaje',
        'reporte__folio',
    )


@admin.register(HistorialReporte)
class HistorialReporteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo HistorialReporte (Bitácora de auditoría activa).
    """
    # Columnas a visualizar para cada entrada de historial de eventos
    list_display = (
        'id',
        'reporte',
        'usuario',
        'accion',
        'fecha',
    )

    # Filtros rápidos disponibles en el panel lateral
    list_filter = (
        'accion',
        'fecha',
    )

    # Criterios de búsqueda habilitados para el historial
    search_fields = (
        'reporte__folio',
        'usuario__username',
        'accion',
        'descripcion',
    )


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Resena (landing page testimonios).
    """
    # Columnas visibles para las reseñas de los ciudadanos
    list_display = (
        'id',
        'usuario',
        'puntuacion',
        'fecha',
    )
    
    # Filtro lateral rápido para buscar por cantidad de estrellas otorgadas o fecha
    list_filter = (
        'puntuacion',
        'fecha',
    )
    
    # Campos de búsqueda textual
    search_fields = (
        'usuario__username',
        'comentario',
    )