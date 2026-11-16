"""Rotas principais do projeto SomTeca.

Cada app tem seu próprio arquivo urls.py; aqui apenas incluímos todos eles.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Textos do cabeçalho do Django Admin
admin.site.site_header = 'SomTeca — Administração'
admin.site.site_title = 'SomTeca Admin'
admin.site.index_title = 'Gerenciamento da biblioteca'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('playlists/', include('playlists.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('', include('musica.urls')),
]

# Em desenvolvimento, o próprio Django serve os arquivos enviados (fotos, capas, mp3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
