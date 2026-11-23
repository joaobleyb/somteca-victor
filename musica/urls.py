"""Rotas do app musica (catálogo, ranking, busca e player)."""
from django.urls import path

from . import views

app_name = 'musica'

urlpatterns = [
    # Página inicial
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Artistas
    path('artistas/', views.ArtistaListView.as_view(), name='artista_lista'),
    path('artistas/novo/', views.ArtistaCreateView.as_view(), name='artista_criar'),
    path('artistas/<int:pk>/', views.ArtistaDetailView.as_view(), name='artista_detalhe'),
    path('artistas/<int:pk>/editar/', views.ArtistaUpdateView.as_view(), name='artista_editar'),
    path('artistas/<int:pk>/excluir/', views.ArtistaDeleteView.as_view(), name='artista_excluir'),

    # Álbuns
    path('albuns/', views.AlbumListView.as_view(), name='album_lista'),
    path('albuns/novo/', views.AlbumCreateView.as_view(), name='album_criar'),
    path('albuns/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detalhe'),
    path('albuns/<int:pk>/editar/', views.AlbumUpdateView.as_view(), name='album_editar'),
    path('albuns/<int:pk>/excluir/', views.AlbumDeleteView.as_view(), name='album_excluir'),

    # Músicas
    path('musicas/', views.MusicaListView.as_view(), name='musica_lista'),
    path('musicas/nova/', views.MusicaCreateView.as_view(), name='musica_criar'),
    path('musicas/<int:pk>/', views.MusicaDetailView.as_view(), name='musica_detalhe'),
    path('musicas/<int:pk>/editar/', views.MusicaUpdateView.as_view(), name='musica_editar'),
    path('musicas/<int:pk>/excluir/', views.MusicaDeleteView.as_view(), name='musica_excluir'),

    # Painel do gestor (só equipe)
    path('gestor/', views.PainelGestorView.as_view(), name='gestor'),

    # Extras
    path('ranking/', views.RankingView.as_view(), name='ranking'),
    path('busca/', views.BuscaView.as_view(), name='busca'),
    path('player/reproducao/<int:pk>/', views.registrar_reproducao, name='registrar_reproducao'),
]
