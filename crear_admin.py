import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_reportes.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
email = "admin@ejemplo.com"
password = "admin123!"  # <-- Cambia esto por la contraseña que quieras

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(">>> SUPERUSUARIO CREADO CON ÉXITO <<<")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(">>> CONTRASEÑA DE SUPERUSUARIO ACTUALIZADA CON ÉXITO <<<")