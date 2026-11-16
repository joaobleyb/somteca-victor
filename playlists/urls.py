"""Rotas do app playlists."""
from django.urls import path

from . import views

app_name = 'playlists'

urlpatterns = [
    path('', views.PlaylistListView.as_view(), name='lista'),
    path('nova/', views.PlaylistCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.PlaylistDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.PlaylistUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.PlaylistDeleteView.as_view(), name='excluir'),

    # Gerenciar as músicas dentro da playlist
    path('<int:pk>/adicionar/', views.adicionar_musica, name='adicionar_musica'),
    path('<int:pk>/itens/<int:item_pk>/remover/', views.remover_item, name='remover_item'),
    path('<int:pk>/itens/<int:item_pk>/<str:direcao>/', views.mover_item, name='mover_item'),
]
