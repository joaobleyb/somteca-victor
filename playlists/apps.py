from django.apps import AppConfig


class PlaylistsConfig(AppConfig):
    """App responsável pelas playlists dos usuários."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'playlists'
    verbose_name = 'Playlists'
