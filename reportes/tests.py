"""
Módulo de Pruebas Unitarias para la aplicación de Reportes.
Contiene casos de prueba automatizados para verificar la autenticación,
creación y actualización de reportes, y visualización de vistas generales.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

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
        self.admin = User.objects.create_superuser(
            username='admin_test',
            password='password123',
            email='admin@example.com'
        )
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
        self.assertTrue('foto' in res_sin_foto.context['form'].errors)

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

    def test_crear_reportes_multiples_categoria_otro(self):
        """
        Prueba que crear múltiples reportes con categoría 'Otro' y nombres personalizados distintos
        generen códigos únicos sin provocar IntegrityError en la base de datos.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='ciudadano_test', password='password123')
        cat_otro, _ = Categoria.objects.get_or_create(nombre='Otro', defaults={'codigo': 'OT'})
        foto_jpg = SimpleUploadedFile('test.jpg', b'jpgcontent', content_type='image/jpeg')
        url = reverse('crear_reporte')

        incidencias = ['Botes llenos', 'Cable suelto']
        for inc in incidencias:
            res = self.client.post(url, {
                'categoria': cat_otro.id,
                'nombre_incidencia_otro': inc,
                'latitud': 16.8531,
                'longitud': -99.8236,
                'calle': 'Costera Miguel Alemán',
                'colonia': 'Centro',
                'codigo_postal': '39300',
                'foto': foto_jpg
            })
            self.assertEqual(res.status_code, 302)

        cat_botes = Categoria.objects.filter(nombre='Botes llenos').first()
        cat_cable = Categoria.objects.filter(nombre='Cable suelto').first()
        self.assertIsNotNone(cat_botes)
        self.assertIsNotNone(cat_cable)
        self.assertNotEqual(cat_botes.codigo, cat_cable.codigo)


class ReabrirEditarReporteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.ciudadano = User.objects.create_user(
            username='citizen_test',
            password='password123',
            email='citizen@example.com'
        )
        # Obtener o actualizar perfil auto-creado por la señal
        self.perfil = self.ciudadano.perfilusuario
        self.perfil.rol = 'ciudadano'
        self.perfil.save()
        self.categoria = Categoria.objects.create(nombre='Alumbrado público', codigo='AP')
        self.reporte = Reporte.objects.create(
            usuario=self.ciudadano,
            categoria=self.categoria,
            titulo='Reporte Alumbrado',
            descripcion='Calle oscura',
            estado='Cancelado',
            latitud=16.8531,
            longitud=-99.8236,
            calle='Costera',
            colonia='Centro',
            codigo_postal='39300'
        )

    def test_editar_reporte_ciudadano_exito(self):
        self.client.login(username='citizen_test', password='password123')
        url = reverse('editar_reporte_ciudadano', kwargs={'id': self.reporte.id})
        
        # Enviar formulario POST modificando la descripción
        response = self.client.post(url, {
            'categoria': self.categoria.id,
            'descripcion': 'Calle muy oscura y peligrosa',
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera Modificada',
            'colonia': 'Centro',
            'codigo_postal': '39300'
        })
        
        self.assertEqual(response.status_code, 302)
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.descripcion, 'Calle muy oscura y peligrosa')
        self.assertEqual(self.reporte.calle, 'Costera Modificada')
        self.assertEqual(self.reporte.estado, 'Pendiente')
        self.assertEqual(self.reporte.intentos_reapertura, 1)

    def test_editar_reporte_ciudadano_limite_intentos(self):
        self.reporte.intentos_reapertura = 2
        self.reporte.save()
        
        self.client.login(username='citizen_test', password='password123')
        url = reverse('editar_reporte_ciudadano', kwargs={'id': self.reporte.id})
        
        response = self.client.post(url, {
            'categoria': self.categoria.id,
            'descripcion': 'Intento fallido',
            'latitud': 16.8531,
            'longitud': -99.8236,
            'calle': 'Costera',
            'colonia': 'Centro',
            'codigo_postal': '39300'
        })
        
        self.assertEqual(response.status_code, 302)
        self.reporte.refresh_from_db()
        # No debió alterarse el estado ni la descripción
        self.assertEqual(self.reporte.estado, 'Cancelado')
        self.assertEqual(self.reporte.intentos_reapertura, 2)

    def test_crear_moderador_rol_inmediato(self):
        admin = User.objects.create_superuser(
            username='admin_creator',
            password='password123',
            email='admin_creator@example.com'
        )
        # Asegurar perfil admin
        admin.perfilusuario.rol = 'administrador'
        admin.perfilusuario.save()

        self.client.login(username='admin_creator', password='password123')
        url = reverse('agregar_usuario')
        
        # Intentar crear un moderador
        response = self.client.post(url, {
            'username': 'nuevo_moderador_test',
            'email': 'mod@example.com',
            'password': 'password123',
            'rol': 'moderador'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el rol sea moderador de forma inmediata en la base de datos
        nuevo_user = User.objects.get(username='nuevo_moderador_test')
        self.assertEqual(nuevo_user.perfilusuario.rol, 'moderador')

    def test_bloqueo_admin_por_moderador_rebotado(self):
        # Crear un moderador y un administrador
        moderador = User.objects.create_user(username='mod_test', password='password123')
        moderador.perfilusuario.rol = 'moderador'
        moderador.perfilusuario.save()

        admin_target = User.objects.create_user(username='admin_target', password='password123')
        admin_target.perfilusuario.rol = 'administrador'
        admin_target.perfilusuario.save()

        self.client.login(username='mod_test', password='password123')
        url = reverse('toggle_bloqueo_usuario', kwargs={'id': admin_target.id})
        
        response = self.client.post(url, {'duracion': 'permanente'})
        self.assertEqual(response.status_code, 302)
        
        admin_target.refresh_from_db()
        # No debió ser bloqueado
        self.assertTrue(admin_target.is_active)

    def test_bloqueo_admin_por_otro_admin_rebotado(self):
        # Crear dos administradores
        admin_req = User.objects.create_user(username='admin_req', password='password123')
        admin_req.perfilusuario.rol = 'administrador'
        admin_req.perfilusuario.save()

        admin_target = User.objects.create_user(username='admin_target2', password='password123')
        admin_target.perfilusuario.rol = 'administrador'
        admin_target.perfilusuario.save()

        self.client.login(username='admin_req', password='password123')
        url = reverse('toggle_bloqueo_usuario', kwargs={'id': admin_target.id})
        
        response = self.client.post(url, {'duracion': '1'})
        self.assertEqual(response.status_code, 302)
        
        admin_target.refresh_from_db()
        # No debió ser bloqueado
        self.assertTrue(admin_target.is_active)

    def test_bloqueo_moderador_por_otro_moderador_rebotado(self):
        # Crear dos moderadores
        mod1 = User.objects.create_user(username='mod_req', password='password123')
        mod1.perfilusuario.rol = 'moderador'
        mod1.perfilusuario.save()

        mod2 = User.objects.create_user(username='mod_target', password='password123')
        mod2.perfilusuario.rol = 'moderador'
        mod2.perfilusuario.save()

        self.client.login(username='mod_req', password='password123')
        url = reverse('toggle_bloqueo_usuario', kwargs={'id': mod2.id})
        
        response = self.client.post(url, {'duracion': 'permanente'})
        self.assertEqual(response.status_code, 302)
        
        mod2.refresh_from_db()
        # No debió ser bloqueado
        self.assertTrue(mod2.is_active)

    def test_bloqueo_moderador_por_admin_exito(self):
        # Crear un admin y un moderador
        admin = User.objects.create_user(username='admin_boss', password='password123')
        admin.perfilusuario.rol = 'administrador'
        admin.perfilusuario.save()

        mod = User.objects.create_user(username='mod_underling', password='password123')
        mod.perfilusuario.rol = 'moderador'
        mod.perfilusuario.save()

        self.client.login(username='admin_boss', password='password123')
        url = reverse('toggle_bloqueo_usuario', kwargs={'id': mod.id})
        
        response = self.client.post(url, {'duracion': 'permanente'})
        self.assertEqual(response.status_code, 302)
        
        mod.refresh_from_db()
        # Debe estar bloqueado/inactivo
        self.assertFalse(mod.is_active)




