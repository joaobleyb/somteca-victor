"""Views do app playlists, separadas em arquivos dentro desta pasta."""
from .item_views import adicionar_musica, mover_item, remover_item
from .playlist_views import (
    PlaylistCreateView, PlaylistDeleteView, PlaylistDetailView, PlaylistListView, PlaylistUpdateView,
)
