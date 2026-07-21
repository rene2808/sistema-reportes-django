"""
Módulo de Enrutamiento (URLs) para la aplicación de Reportes.
Asocia las rutas del navegador con sus respectivas funciones de vista
en views.py.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Vistas Públicas e Inicio ---
    path('', views.inicio, name='inicio'),
    path('login/', views.login_usuario, name='login'),

    # --- Autenticación y Registro ---
    path('registro/', views.registro_usuario, name='registro'),
    path('verificar-correo/', views.verificar_correo, name='verificar_correo'),
    path('verificar-usuario/', views.verificar_usuario, name='verificar_usuario'),
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # --- Recuperación de Contraseña (Vistas nativas basadas en clases de Django) ---
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='reportes/password_reset_form.html',
        email_template_name='reportes/password_reset_email.html',
        subject_template_name='reportes/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='reportes/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='reportes/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='reportes/password_reset_complete.html'
    ), name='password_reset_complete'),

    # --- Paneles de Control (Dashboards) ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('panel/ciudadano/', views.panel_ciudadano, name='panel_ciudadano'),
    path('panel/administrador/', views.panel_administrador, name='panel_administrador'),

    # --- Gestión del Perfil de Usuario ---
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # --- Operaciones de Reportes (CRUD y PDF) ---
    path('reporte/nuevo/', views.crear_reporte, name='crear_reporte'),
    path('reporte/<int:id>/', views.detalle_reporte, name='detalle_reporte'),
    path('reporte/<int:id>/pdf/', views.reporte_individual_pdf, name='reporte_individual_pdf'),
    path('reportes/mensual/pdf/', views.reporte_mensual_incidentes_pdf, name='reporte_mensual_incidentes_pdf'),
    path('reportes/mensual/excel/', views.reporte_mensual_incidentes_excel, name='reporte_mensual_incidentes_excel'),
    path('reporte/<int:id>/estado/', views.cambiar_estado_reporte, name='cambiar_estado'),
    path('reporte/<int:id>/prioridad/', views.cambiar_prioridad_reporte, name='cambiar_prioridad'),
    path('reporte/<int:id>/actualizar/', views.actualizar_reporte, name='actualizar_reporte'),
    path('reporte/<int:id>/evidencia/', views.agregar_evidencia, name='agregar_evidencia'),
    path('reporte/<int:id>/eliminar/', views.eliminar_reporte, name='eliminar_reporte'),

    # --- Gestión de Usuarios (Administración) ---
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/<int:id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/<int:id>/toggle-bloqueo/', views.toggle_bloqueo_usuario, name='toggle_bloqueo_usuario'),
    path('resena/<int:id>/eliminar/', views.eliminar_resena, name='eliminar_resena'),

    # --- Configuración de Catálogos e Informes ---
    path('categorias/agregar/', views.agregar_catalogo, {'catalogo': 'categoria'}, name='agregar_categoria'),
    path('categorias/<int:id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('reporte-general/', views.reporte_general, name='reporte_general'),

    # --- Notificaciones ---
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('notificaciones/<int:id>/abrir/', views.abrir_notificacion, name='abrir_notificacion'),
    path('notificaciones/<int:id>/marcar-leida/', views.marcar_notificacion_leida_individual, name='marcar_notificacion_leida_individual'),
    path('notificaciones/<int:id>/eliminar/', views.eliminar_notificacion, name='eliminar_notificacion'),
    path('notificaciones/leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
    path('api/notificaciones/sin-leer/', views.api_notificaciones_sin_leer, name='api_notificaciones_sin_leer'),
    path('api/usuarios/estados/', views.api_estado_usuarios, name='api_estado_usuarios'),

    # --- Galería Pública y Reseñas ---
    path('resena/nueva/', views.dejar_reseña, name='dejar_reseña'),
    path('reporte/<int:id>/fotos-galeria/', views.editar_fotos_galeria, name='editar_fotos_galeria'),
    path('reporte/<int:id>/fotos-galeria/eliminar/', views.eliminar_fotos_galeria, name='eliminar_fotos_galeria'),
    path('reporte/<int:id>/fotos-galeria/toggle/', views.toggle_mostrar_galeria, name='toggle_mostrar_galeria'),
    path('contacto/', views.enviar_contacto_correo, name='contacto'),
]