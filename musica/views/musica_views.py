"""CRUD de músicas, com filtro por gênero."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ..forms import MusicaForm
from ..models import GENEROS, Album, Musica
from .mixins import ExclusaoMixin, FormularioMixin, VoltarParaNextMixin


class MusicaListView(ListView):
    """Lista as músicas em cards. Aceita ?genero=rock para filtrar pelo gênero."""
    model = Musica
    template_name = 'musica/musica/lista.html'
    context_object_name = 'musicas'
    paginate_by = settings.ITENS_POR_PAGINA

    def get_queryset(self):
        musicas = (
            Musica.objects
            .select_related('album')
            .prefetch_related('artistas')
            .order_by('titulo')
        )
        genero = self.request.GET.get('genero', '')
        if genero:
            # O gênero fica no álbum, então filtramos "atravessando" a ForeignKey
            musicas = musicas.filter(album__genero=genero)
        return musicas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['generos'] = GENEROS
        contexto['genero_selecionado'] = self.request.GET.get('genero', '')
        return contexto


class MusicaDetailView(DetailView):
    model = Musica
    template_name = 'musica/musica/detalhe.html'
    context_object_name = 'musica'

    def get_queryset(self):
        return Musica.objects.select_related('album__artista').prefetch_related('artistas')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Fila do player contendo só esta música
        contexto['musica_unica'] = [self.object]
        # Outras faixas do mesmo álbum
        contexto['outras_faixas'] = (
            self.object.album.musicas
            .exclude(pk=self.object.pk)
            .select_related('album')
            .prefetch_related('artistas')
        )
        return contexto


class MusicaCreateView(LoginRequiredMixin, VoltarParaNextMixin, FormularioMixin, CreateView):
    model = Musica
    form_class = MusicaForm
    titulo_pagina = 'Cadastrar música'
    success_message = 'Música "%(objeto)s" cadastrada com sucesso!'

    def get_initial(self):
        # Permite abrir o formulário já com o álbum escolhido: ?album=5
        inicial = super().get_initial()
        album_id = self.request.GET.get('album', '')
        if album_id.isdigit():
            album = Album.objects.filter(pk=album_id).first()
            if album:
                inicial['album'] = album
                inicial['artistas'] = [album.artista]
                inicial['numero_faixa'] = album.musicas.count() + 1
        return inicial


class MusicaUpdateView(LoginRequiredMixin, VoltarParaNextMixin, FormularioMixin, UpdateView):
    model = Musica
    form_class = MusicaForm
    titulo_pagina = 'Editar música'
    success_message = 'Música "%(objeto)s" atualizada com sucesso!'


class MusicaDeleteView(LoginRequiredMixin, VoltarParaNextMixin, ExclusaoMixin, DeleteView):
    model = Musica
    tipo_objeto = 'a música'
    success_url = reverse_lazy('musica:musica_lista')
    success_message = 'Música "%(objeto)s" excluída com sucesso!'
