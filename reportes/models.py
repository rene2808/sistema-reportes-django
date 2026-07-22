"""
Módulo de Modelos para la aplicación de Reportes.
Define la estructura de datos y las relaciones de la base de datos,
incluyendo categorías, perfiles de usuario, reportes, evidencias,
notificaciones y reseñas.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Categoria(models.Model):
    """
    Representa las categorías generales de los reportes viales y urbanos (ej. Basura, Baches).
    """
    # Mapeo de códigos internos a nombres descriptivos legibles de categorías
    CODIGOS = [
        ('BS', 'Basura'),
        ('BV', 'Baches en Vía Pública'),
        ('FE', 'Fallos de electricidad'),
        ('FA', 'Fugas de agua'),
        ('AP', 'Alumbrado público'),
        ('SD', 'Semáforo dañado'),
    ]

    # Nombre oficial y único de la categoría (ej: "Fugas de agua")
    nombre = models.CharField(max_length=100, unique=True)
    
    # Código corto de dos letras para identificar la categoría en el folio del reporte
    codigo = models.CharField(max_length=5, choices=CODIGOS, unique=True)

    def __str__(self):
        # Retorna el nombre de la categoría para representación en texto
        return self.nombre
    
class TipoProblema(models.Model):
    """
    [LEGACY / NO UTILIZADO] Especifica los tipos específicos de problemas que pertenecen a una categoría.
    """
    # Relación de llave foránea con el modelo Categoria
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='tipos_problema'
    )

    # Nombre específico del problema urbano
    nombre = models.CharField(max_length=100)

    class Meta:
        # Restricción única para evitar nombres duplicados dentro de la misma categoría
        unique_together = ('categoria', 'nombre')

    def __str__(self):
        # Retorna la representación del problema con su categoría
        return f'{self.categoria.nombre} - {self.nombre}'
    
class EstadoReporte(models.Model):
    """
    [LEGACY / NO UTILIZADO] Define los posibles estados de flujo de un reporte vial (ej. Pendiente, En Proceso, Completado).
    """
    # Nombre único del estado del reporte
    nombre = models.CharField(max_length=50, unique=True)
    
    # Orden de aparición en listados y flujos lógicos
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        # Retorna el nombre del estado
        return self.nombre


class Prioridad(models.Model):
    """
    [LEGACY / NO UTILIZADO] Define los niveles de prioridad de un reporte (ej. Baja, Media, Alta, Crítica).
    """
    # Nombre del nivel de prioridad
    nombre = models.CharField(max_length=50, unique=True)
    
    # Nivel numérico de severidad para ordenamiento (a mayor número, mayor severidad)
    nivel = models.PositiveIntegerField(default=1)

    def __str__(self):
        # Retorna el nombre del nivel de prioridad
        return self.nombre

class Rol(models.Model):
    """
    [LEGACY / NO UTILIZADO] Modelo heredado/catálogo para roles del sistema (Legacy).
    """
    # Nombre del rol del sistema
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        # Retorna el nombre del rol
        return self.nombre
    
class PerfilUsuario(models.Model):
    """
    Almacena información adicional y el rol administrativo/ciudadano de cada usuario en el sistema.
    """
    # Lista de roles disponibles en el sistema para la gestión y permisos de usuario
    ROLES = [
        ('ciudadano', 'Ciudadano'),
        ('moderador', 'Moderador de Contenido'),
        ('administrador', 'Administrador'),
    ]

    # Relación uno a uno con el modelo de Usuario integrado en Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Rol actual del usuario, por defecto es un ciudadano común
    rol = models.CharField(max_length=30, choices=ROLES, default='ciudadano')
    
    # Número de teléfono del usuario para fines de contacto o seguimiento
    telefono = models.CharField(max_length=20, blank=True, null=True)

    # Fecha y hora de su última actividad en el sistema para determinar si está en línea
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # Muestra el nombre de usuario de Django y su rol correspondiente
        return f'{self.usuario.username} - {self.get_rol_display()}'

    @property
    def esta_en_linea(self):
        """
        Determina si el usuario está en línea basado en su última actividad
        registrada en la base de datos (vigente por 10 minutos).
        Usa marcas de tiempo POSIX (timestamp) para evitar cualquier discrepancia de zona horaria.
        """
        if self.ultimo_acceso:
            from django.utils import timezone
            try:
                diferencia = timezone.now().timestamp() - self.ultimo_acceso.timestamp()
                return 0 <= diferencia < 600
            except Exception:
                return False
        return False


# --- Señales de Django (Signals) ---

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal que crea de forma automática un PerfilUsuario cuando un nuevo Usuario es registrado.
    """
    if created:
        PerfilUsuario.objects.get_or_create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Señal que guarda el PerfilUsuario asociado cada vez que el objeto de Usuario se actualice.
    """
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()


class Reporte(models.Model):
    """
    Modelo principal que representa la información técnica, geográfica y fotográfica de una incidencia reportada.
    """
    # Lista de estados posibles por los que puede pasar un reporte ciudadano
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En proceso', 'En proceso'),
        ('Resuelto', 'Resuelto'),
        ('Cancelado', 'Cancelado'),
    ]

    # Lista de niveles de urgencia o prioridad para la atención de incidentes
    PRIORIDADES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    # Folio identificador único generado dinámicamente al guardar el reporte
    folio = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        null=True,
        editable=False
    )

    # Usuario ciudadano que creó el reporte original
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reportes'
    )

    # Categoría asociada al problema reportado (ej. Basura, Baches)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='reportes'
    )

    # Título o encabezado breve del reporte (ej: "Reporte de Basura")
    titulo = models.CharField(max_length=150, blank=True, null=True)
    
    # Descripción detallada proporcionada por el ciudadano sobre el incidente
    descripcion = models.TextField(blank=True, null=True)

    # Ubicación: Municipio en el que se ubica el reporte (por defecto Acapulco)
    municipio = models.CharField(max_length=100, default='Acapulco de Juárez')
    
    # Ubicación: Nombre de la colonia recopilada mediante el mapa o dirección
    colonia = models.CharField(max_length=100, blank=True, null=True)
    
    # Ubicación: Nombre de la calle de la incidencia
    calle = models.CharField(max_length=100, blank=True, null=True)
    
    # Ubicación: Código postal de la colonia
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    # Ubicación: Referencias adicionales (ej. "frente al OXXO")
    referencia = models.TextField(blank=True, null=True)

    # Ubicación Geográfica: Latitud capturada por el mapa Leaflet
    latitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    
    # Ubicación Geográfica: Longitud capturada por el mapa Leaflet
    longitud = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    # Nivel de prioridad asignado al reporte, por defecto es Media
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='Media')
    
    # Estado actual del reporte en el flujo del sistema, por defecto es Pendiente
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    # Fotografía inicial ("Antes") del incidente subida por el ciudadano
    foto = models.ImageField(upload_to='reportes/', blank=True, null=True)

    # Fecha y hora exacta de creación del reporte (se asigna automáticamente)
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    # Indica si el reporte resuelto debe mostrarse públicamente en la galería de la landing page
    mostrar_en_galeria = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar un Folio único y estructurado 
        (ej: REP-YYYYMMDD-00001) tras guardar por primera vez.
        """
        if not self.folio:
            # Primero guarda para obtener un ID autoincrementable de base de datos
            super().save(*args, **kwargs)

            # Estructurar la fecha del día actual evitando NoneType
            fecha_ref = self.fecha_reporte or timezone.now()
            fecha = fecha_ref.strftime('%Y%m%d')
            # Concatenar prefijo, fecha e ID con relleno a 5 dígitos
            folio_generado = f'REP-{fecha}-{self.id:05d}'

            # Asignar y guardar el folio en la base de datos
            self.folio = folio_generado
            Reporte.objects.filter(pk=self.pk).update(folio=folio_generado)
        else:
            # Si el folio ya existe, realiza un guardado convencional
            super().save(*args, **kwargs)

    def __str__(self):
        # Representa el reporte con su folio y título en textos descriptivos
        return f'{self.folio} - {self.titulo}'


class Evidencia(models.Model):
    """
    Representa imágenes adicionales ("Después" o avances) de reparación subidas por administradores o moderadores.
    """
    # Reporte asociado al que pertenece esta evidencia fotográfica
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )

    # Archivo de imagen subido al servidor (carpeta /media/evidencias/)
    archivo = models.ImageField(upload_to='evidencias/')
    
    # Descripción o comentario sobre la evidencia (ej: "Bache pavimentado")
    descripcion = models.TextField(blank=True, null=True)
    
    # Fecha y hora en la que se subió la evidencia fotográfica
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Retorna una descripción indicando el folio del reporte
        return f'Evidencia de {self.reporte.folio}'

class HistorialCambio(models.Model):
    """
    [LEGACY / NO UTILIZADO] Registraba cambios anteriores de estado y prioridad (reemplazado por HistorialReporte).
    """
    # Reporte sobre el cual se hizo el cambio
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='historial'
    )

    # Usuario administrador o moderador que realizó la actualización
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_cambios'
    )

    # Acción realizada en el cambio (ej. "Actualización de prioridad")
    accion = models.CharField(max_length=150)
    
    # Detalle descriptivo de los cambios hechos
    descripcion = models.TextField(blank=True, null=True)

    # Relación foránea legacy con el estado anterior del reporte
    estado_anterior = models.ForeignKey(
        EstadoReporte,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_estado_anterior'
    )

    # Relación foránea legacy con el estado nuevo asignado
    estado_nuevo = models.ForeignKey(
        EstadoReporte,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_estado_nuevo'
    )

    # Relación foránea legacy con la prioridad anterior
    prioridad_anterior = models.ForeignKey(
        Prioridad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_prioridad_anterior'
    )

    # Relación foránea legacy con la prioridad nueva asignada
    prioridad_nueva = models.ForeignKey(
        Prioridad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='historial_prioridad_nueva'
    )

    # Fecha exacta del cambio registrado en el historial
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Representa el registro de cambio con el folio del reporte y acción
        return f'{self.reporte.folio} - {self.accion}'
    
class Notificacion(models.Model):
    """
    Alertas y avisos en el sistema dirigidos a usuarios para comunicar actualizaciones sobre incidentes.
    """
    # Usuario receptor de la notificación
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )

    # Reporte relacionado al que hace referencia la notificación (opcional)
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        blank=True,
        null=True
    )

    # Encabezado o título corto del aviso (ej: "Reporte Resuelto")
    titulo = models.CharField(max_length=150)
    
    # Mensaje detallado de la notificación
    mensaje = models.TextField()
    
    # Estado de lectura de la notificación por el usuario
    leida = models.BooleanField(default=False)
    
    # Fecha de creación del aviso
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Representa la notificación con el nombre del usuario y el título
        return f'{self.usuario.username} - {self.titulo}'


class HistorialReporte(models.Model):
    """
    Historial de auditoría para rastrear el ciclo de vida, validaciones y cambios de cada reporte en el sistema.
    """
    # Reporte al que pertenece esta bitácora o evento de historial
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='historial_eventos'
    )

    # Usuario que realizó la acción sobre el reporte (puede ser nulo si es una acción automática)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    # Acción principal efectuada (ej: "Reporte registrado", "Cambio de estado")
    accion = models.CharField(max_length=150)
    
    # Nota o descripción del historial
    descripcion = models.TextField(blank=True, null=True)
    
    # Fecha y hora en la que se generó la entrada de historial
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Representa la entrada con el folio del reporte y la acción realizada
        return f'{self.reporte.folio} - {self.accion}'


class Resena(models.Model):
    """
    Calificación y opinión escrita que los ciudadanos dejan sobre la plataforma o sobre el servicio.
    Puede estar vinculada a un reporte resuelto y adjuntar hasta 2 fotos de evidencia del resultado.
    """
    # Usuario que emite la opinión en la landing page
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reseñas'
    )

    # Reporte resuelto asociado a la reseña (opcional)
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reseñas'
    )
    
    # Comentario escrito de la opinión
    comentario = models.TextField()
    
    # Calificación numérica del 1 al 5 estrellas asignada por el ciudadano
    puntuacion = models.IntegerField(default=5)

    # Evidencias fotográficas adjuntas por el ciudadano en su reseña (máximo 2)
    foto1 = models.ImageField(upload_to='resenas/', blank=True, null=True)
    foto2 = models.ImageField(upload_to='resenas/', blank=True, null=True)
    
    # Fecha de emisión de la reseña
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Retorna el usuario y la puntuación otorgada
        return f'{self.usuario.username} - {self.puntuacion} estrellas'