"""
Módulo de Pruebas Unitarias para la aplicación de Reportes.
Contiene casos de prueba automatizados para verificar la autenticación,
creación y actualización de reportes, y visualización de vistas generales.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class VerificarUsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='usuario_prueba',
            password='password123',
            email='test@example.com'
        )

    def test_verificar_usuario_existe(self):
        url = reverse('verificar_usuario')
        response = self.client.get(url, {'username': 'usuario_prueba'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'existe': True})

    def test_verificar_usuario_no_existe(self):
        url = reverse('verificar_usuario')
        response = self.client.get(url, {'username': 'usuario_inexistente'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'existe': False})

    def test_verificar_usuario_vacio(self):
        url = reverse('verificar_usuario')
        response = self.client.get(url, {'username': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'existe': False})


from .models import Categoria, Reporte, PerfilUsuario, Notificacion

class ActualizarReporteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            email='admin@example.com'
        )
        # Asignar el rol de administrador al perfil de usuario creado
        perfil = self.admin.perfilusuario
        perfil.rol = 'administrador'
        perfil.save()

        self.ciudadano = User.objects.create_user(
            username='ciudadano_test',
            password='password123',
            email='ciudadano@example.com'
        )
        # Se requiere crear al menos una categoría para poder generar un Reporte
        self.categoria = Categoria.objects.create(
            nombre='Baches',
            codigo='BV'
        )

        self.reporte = Reporte.objects.create(
            usuario=self.ciudadano,
            categoria=self.categoria,
            titulo='Bache grande',
            prioridad='Media',
            estado='Pendiente'
        )

    def test_actualizar_reporte_estado_y_prioridad(self):
        self.client.login(username='admin_test', password='password123')
        url = reverse('actualizar_reporte', args=[self.reporte.id])
        
        response = self.client.post(url, {
            'estado': 'En proceso',
            'prioridad': 'Alta'
        })
        self.assertEqual(response.status_code, 302) # Redirige al detalle del reporte
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.estado, 'En proceso')
        self.assertEqual(self.reporte.prioridad, 'Alta')

        # Verificar que se ha creado correctamente una notificación para el ciudadano
        notif = Notificacion.objects.filter(usuario=self.ciudadano).first()
        self.assertIsNotNone(notif)
        self.assertIn('de estado (Pendiente a En proceso)', notif.mensaje)
        self.assertIn('de prioridad (Media a Alta)', notif.mensaje)

    def test_actualizar_reporte_solo_estado(self):
        self.client.login(username='admin_test', password='password123')
        url = reverse('actualizar_reporte', args=[self.reporte.id])
        
        response = self.client.post(url, {
            'estado': 'Cancelado',
            'prioridad': 'Media' # Sin cambios en prioridad
        })
        self.assertEqual(response.status_code, 302)
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.estado, 'Cancelado')
        self.assertEqual(self.reporte.prioridad, 'Media')

        notif = Notificacion.objects.filter(usuario=self.ciudadano).first()
        self.assertIsNotNone(notif)
        self.assertIn('de estado (Pendiente a Cancelado)', notif.mensaje)
        self.assertNotIn('prioridad', notif.mensaje)

    def test_actualizar_reporte_sin_cambios(self):
        self.client.login(username='admin_test', password='password123')
        url = reverse('actualizar_reporte', args=[self.reporte.id])
        
        response = self.client.post(url, {
            'estado': 'Pendiente',
            'prioridad': 'Media'
        })
        self.assertEqual(response.status_code, 302)
        
        notif = Notificacion.objects.filter(usuario=self.ciudadano).first()
        self.assertIsNone(notif) # No se genera ninguna notificación si no hay cambios reales

    def test_actualizar_reporte_con_evidencia(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import Evidencia
        self.client.login(username='admin_test', password='password123')
        url = reverse('actualizar_reporte', args=[self.reporte.id])
        
        imagen_mock = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'mock_image_data',
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {
            'estado': 'Resuelto',
            'prioridad': 'Urgente',
            'archivo': imagen_mock,
            'descripcion': 'Bache reparado temporalmente'
        })
        self.assertEqual(response.status_code, 302)
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.estado, 'Resuelto')
        self.assertEqual(self.reporte.prioridad, 'Urgente')
        
        evidencia = Evidencia.objects.filter(reporte=self.reporte).first()
        self.assertIsNotNone(evidencia)
        self.assertEqual(evidencia.descripcion, 'Bache reparado temporalmente')
        self.assertTrue(evidencia.archivo.name.endswith('test_image.jpg'))
        
        if evidencia.archivo:
            evidencia.archivo.delete(save=False)


class ReporteGeneralTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            email='admin@example.com'
        )
        perfil = self.admin.perfilusuario
        perfil.rol = 'administrador'
        perfil.save()

        self.ciudadano = User.objects.create_user(
            username='ciudadano_test',
            password='password123',
            email='ciudadano@example.com'
        )

        # Crear múltiples categorías para verificar la clasificación
        self.cat_baches = Categoria.objects.create(nombre='Baches', codigo='BV')
        self.cat_electricidad = Categoria.objects.create(nombre='Fallos de electricidad', codigo='FE')

        # Crear reportes bajo diferentes categorías de incidencias
        Reporte.objects.create(
            usuario=self.ciudadano,
            categoria=self.cat_baches,
            titulo='Bache grande',
            prioridad='Media',
            estado='Pendiente'
        )
        Reporte.objects.create(
            usuario=self.ciudadano,
            categoria=self.cat_electricidad,
            titulo='Poste caído',
            prioridad='Alta',
            estado='En proceso'
        )

    def test_reporte_general_categorizacion_dinamica(self):
        self.client.login(username='admin_test', password='password123')
        url = reverse('reporte_general')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que las categorías dinámicas existan en el contexto de respuesta
        reportes_por_categoria = response.context['reportes_por_categoria']
        self.assertEqual(len(reportes_por_categoria), 2)

        # Verificar detalles de la primera categoría (ordenada por nombre: Baches primero, Fallos de electricidad segundo)
        baches_grupo = reportes_por_categoria[0]
        self.assertEqual(baches_grupo['categoria'].nombre, 'Baches')
        self.assertEqual(baches_grupo['total'], 1)
        self.assertEqual(baches_grupo['pendientes'], 1)

        # Verificar detalles de la segunda categoría
        elec_grupo = reportes_por_categoria[1]
        self.assertEqual(elec_grupo['categoria'].nombre, 'Fallos de electricidad')
        self.assertEqual(elec_grupo['total'], 1)
        self.assertEqual(elec_grupo['en_proceso'], 1)


class CrearReporteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.ciudadano = User.objects.create_user(
            username='ciudadano_test',
            password='password123',
            email='ciudadano@example.com'
        )
        from .views import crear_catalogos_iniciales
        crear_catalogos_iniciales()
        self.cat = Categoria.objects.get(codigo='BV')

    def test_crear_reporte_redireccion_y_sin_notificacion_ciudadano(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='ciudadano_test', password='password123')
        url = reverse('crear_reporte')
        
        foto_mock = SimpleUploadedFile(
            name='evidencia.jpg',
            content=b'\xFF\xD8\xFF\xE0\x00\x10JFIF',
            content_type='image/jpeg'
        )

        response = self.client.post(url, {
            'categoria': self.cat.id,
            'descripcion': 'Bache profundo en avenida principal',
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera',
            'colonia': 'Centro',
            'codigo_postal': '39300',
            'foto': foto_mock
        })
        
        reporte = Reporte.objects.first()
        self.assertIsNotNone(reporte)
        expected_url = f"{reverse('detalle_reporte', args=[reporte.id])}?creado=1"
        self.assertRedirects(response, expected_url)
        
        notif_ciudadano = Notificacion.objects.filter(usuario=self.ciudadano, titulo='Reporte recibido').first()
        self.assertIsNone(notif_ciudadano)

    def test_crear_reporte_validacion_fotos_jpg(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='ciudadano_test', password='password123')
        url = reverse('crear_reporte')

        # 1. Intento sin foto (Debe fallar)
        res_sin_foto = self.client.post(url, {
            'categoria': self.cat.id,
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera',
            'colonia': 'Centro',
            'codigo_postal': '39300'
        })
        self.assertEqual(res_sin_foto.status_code, 200)
        self.assertFormError(res_sin_foto, 'form', 'foto', 'Este campo es obligatorio.')

        # 2. Intento con formato PNG no permitido (Debe fallar)
        foto_png = SimpleUploadedFile('prueba.png', b'pngcontent', content_type='image/png')
        res_png = self.client.post(url, {
            'categoria': self.cat.id,
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera',
            'colonia': 'Centro',
            'codigo_postal': '39300',
            'foto': foto_png
        })
        self.assertEqual(res_png.status_code, 200)
        self.assertContains(res_png, 'no está en formato JPG')

    def test_notificaciones_no_marca_leida_automaticamente(self):
        self.client.login(username='ciudadano_test', password='password123')
        notif = Notificacion.objects.create(
            usuario=self.ciudadano,
            titulo='Test Notificacion',
            mensaje='Mensaje de prueba',
            leida=False
        )
        response = self.client.get(reverse('notificaciones'))
        self.assertEqual(response.status_code, 200)
        notif.refresh_from_db()
        self.assertFalse(notif.leida)

    def test_marcar_notificacion_leida_individual(self):
        self.client.login(username='ciudadano_test', password='password123')
        notif = Notificacion.objects.create(
            usuario=self.ciudadano,
            titulo='Test Notificacion',
            mensaje='Mensaje de prueba',
            leida=False
        )
        response = self.client.get(reverse('marcar_notificacion_leida_individual', args=[notif.id]))
        self.assertEqual(response.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.leida)

    def test_eliminar_notificacion_individual(self):
        self.client.login(username='ciudadano_test', password='password123')
        notif = Notificacion.objects.create(
            usuario=self.ciudadano,
            titulo='Test Notificacion',
            mensaje='Mensaje de prueba',
            leida=False
        )
        response = self.client.post(reverse('eliminar_notificacion', args=[notif.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Notificacion.objects.filter(id=notif.id).exists())

    def test_reporte_mensual_excel_generacion(self):
        self.client.login(username='admin_test', password='password123')
        url = reverse('reporte_mensual_incidentes_excel')
        response = self.client.get(url, {'mes': 7, 'anio': 2026})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_crear_reporte_categoria_otro(self):
        self.client.login(username='ciudadano_test', password='password123')
        cat_otro, _ = Categoria.objects.get_or_create(nombre='Otro', defaults={'codigo': 'OT'})
        foto_jpg = SimpleUploadedFile('test.jpg', b'jpgcontent', content_type='image/jpeg')
        url = reverse('crear_reporte')
        response = self.client.post(url, {
            'categoria': cat_otro.id,
            'nombre_incidencia_otro': 'Árbol Caído',
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera Miguel Alemán',
            'colonia': 'Centro',
            'codigo_postal': '39300',
            'foto': foto_jpg
        })
        self.assertEqual(response.status_code, 302)
        reporte_creado = Reporte.objects.filter(usuario=self.ciudadano).latest('id')
        self.assertEqual(reporte_creado.categoria.nombre, 'Árbol caído')
