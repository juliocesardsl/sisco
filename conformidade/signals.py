import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_admin_user(sender, **kwargs):
    """Cria um superusuário padrão quando o banco ainda não possui nenhum admin."""
    if sender.name != 'conformidade':
        return

    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return

    username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@sisconformidade.local')
    password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')

    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )

    print(f'Usuário administrador padrão criado: {username}')
