"""Configuração do Django Admin para playlists."""
from django.contrib import admin

from .models import ItemPlaylist, Playlist


class ItemPlaylistInline(admin.TabularInline):
    """Mostra as músicas da playlist (com a ordem) dentro da própria playlist."""
    model = ItemPlaylist
    extra = 1
    fields = ['ordem', 'musica', 'adicionada_em']
    readonly_fields = ['adicionada_em']
    autocomplete_fields = ['musica']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'publica', 'qtd_musicas', 'data_criacao']
    search_fields = ['nome', 'descricao', 'usuario__username']
    list_filter = ['publica', 'data_criacao', 'usuario']
    list_editable = ['publica']
    list_select_related = ['usuario']
    inlines = [ItemPlaylistInline]

    @admin.display(description='músicas')
    def qtd_musicas(self, obj):
        return obj.itens.count()


@admin.register(ItemPlaylist)
class ItemPlaylistAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'ordem', 'musica', 'adicionada_em']
    search_fields = ['playlist__nome', 'musica__titulo']
    list_filter = ['playlist', 'adicionada_em']
    list_select_related = ['playlist', 'musica']
