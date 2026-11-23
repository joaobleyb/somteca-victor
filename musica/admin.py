"""Configuração do Django Admin para o catálogo musical."""
from django.contrib import admin

from .models import Album, Artista, Musica, Reproducao


@admin.action(description='Aprovar os itens selecionados')
def aprovar_selecionados(modeladmin, request, queryset):
    total = queryset.update(aprovado=True)
    modeladmin.message_user(request, f'{total} item(ns) aprovado(s).')


class AlbumInline(admin.TabularInline):
    """Permite ver/editar os álbuns direto na página do artista."""
    model = Album
    extra = 0
    fields = ['titulo', 'ano_lancamento', 'genero']


class MusicaInline(admin.TabularInline):
    """Permite ver/editar as faixas direto na página do álbum."""
    model = Musica
    extra = 0
    fields = ['numero_faixa', 'titulo', 'duracao', 'total_reproducoes']
    readonly_fields = ['total_reproducoes']


@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais_origem', 'qtd_albuns', 'aprovado', 'enviado_por', 'data_criacao']
    search_fields = ['nome', 'pais_origem', 'biografia']
    list_filter = ['aprovado', 'pais_origem', 'data_criacao']
    inlines = [AlbumInline]
    actions = [aprovar_selecionados]
    readonly_fields = ['enviado_por']

    @admin.display(description='álbuns')
    def qtd_albuns(self, obj):
        return obj.albuns.count()


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'artista', 'ano_lancamento', 'genero', 'qtd_musicas', 'aprovado']
    search_fields = ['titulo', 'artista__nome']
    list_filter = ['aprovado', 'genero', 'ano_lancamento', 'artista']
    list_select_related = ['artista']
    inlines = [MusicaInline]
    actions = [aprovar_selecionados]
    readonly_fields = ['enviado_por']

    @admin.display(description='músicas')
    def qtd_musicas(self, obj):
        return obj.musicas.count()


@admin.register(Musica)
class MusicaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'album', 'numero_faixa', 'duracao_formatada', 'total_reproducoes', 'aprovado']
    search_fields = ['titulo', 'album__titulo', 'artistas__nome']
    list_filter = ['aprovado', 'album__genero', 'album__ano_lancamento', 'artistas']
    list_select_related = ['album']
    filter_horizontal = ['artistas']
    actions = [aprovar_selecionados]
    readonly_fields = ['enviado_por']

    @admin.display(description='duração')
    def duracao_formatada(self, obj):
        return obj.duracao_formatada


@admin.register(Reproducao)
class ReproducaoAdmin(admin.ModelAdmin):
    list_display = ['musica', 'usuario', 'data_hora']
    search_fields = ['musica__titulo', 'usuario__username']
    list_filter = ['data_hora', 'usuario']
    list_select_related = ['musica', 'usuario']
    date_hierarchy = 'data_hora'
    autocomplete_fields = ['musica']
