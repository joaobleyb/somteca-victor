"""
Views do app musica, separadas por assunto em arquivos dentro desta pasta.

Este __init__ reexporta todas as views para que o urls.py possa usar
`from . import views` e depois `views.ArtistaListView`, por exemplo.
"""
from .album_views import (
    AlbumCreateView, AlbumDeleteView, AlbumDetailView, AlbumListView, AlbumUpdateView,
)
from .artista_views import (
    ArtistaCreateView, ArtistaDeleteView, ArtistaDetailView, ArtistaListView, ArtistaUpdateView,
)
from .busca_views import BuscaView
from .dashboard_views import DashboardView
from .gestor_views import PainelGestorView, aprovar
from .musica_views import (
    MusicaCreateView, MusicaDeleteView, MusicaDetailView, MusicaListView, MusicaUpdateView,
)
from .player_views import registrar_reproducao
