from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """App de autenticação (cadastro, login, logout) e da retrospectiva do usuário."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    verbose_name = 'Usuários'
