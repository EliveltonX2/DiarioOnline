import os
import django

# Configura o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dion_project.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('ADMIN_USERNAME', 'admin')
password = os.environ.get('ADMIN_PASSWORD', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

if not User.objects.filter(username=username).exists():
    print(f"Criando superusuario '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario criado com sucesso!")
else:
    print(f"Superusuario '{username}' ja existe. Nenhuma acao tomada.")
