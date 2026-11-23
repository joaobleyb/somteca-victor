from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """App de autenticação (cadastro, login, logout)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    verbose_name = 'Usuários'
