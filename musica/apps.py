from django.apps import AppConfig


class MusicaConfig(AppConfig):
    """App responsável pelo catálogo: artistas, álbuns, músicas e reproduções."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'musica'
    verbose_name = 'Catálogo musical'
