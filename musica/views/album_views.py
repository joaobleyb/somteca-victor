"""CRUD de álbuns, com filtro por ano de lançamento."""
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ..forms import AlbumForm
from ..models import Album
from .mixins import (
    CadastroComAprovacaoMixin, ExclusaoMixin, FormularioMixin, GestorRequiredMixin, SoAprovadosMixin,
    VoltarParaNextMixin,
)


class AlbumListView(ListView):
    """Lista os álbuns em cards. Aceita ?ano=2020 para filtrar pelo ano."""
    model = Album
    template_name = 'musica/album/lista.html'
    context_object_name = 'albuns'
    paginate_by = settings.ITENS_POR_PAGINA

    def get_queryset(self):
        albuns = Album.objects.aprovados().select_related('artista')
        ano = self.request.GET.get('ano', '')
        if ano.isdigit():
            albuns = albuns.filter(ano_lancamento=int(ano))
        return albuns

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        # Lista de anos existentes, para montar o <select> do filtro
        contexto['anos'] = (
            Album.objects.aprovados().order_by('-ano_lancamento')
            .values_list('ano_lancamento', flat=True)
            .distinct()
        )
        contexto['ano_selecionado'] = self.request.GET.get('ano', '')
        return contexto


class AlbumDetailView(SoAprovadosMixin, DetailView):
    """Página do álbum com a lista de faixas, pronta para tocar."""
    model = Album
    template_name = 'musica/album/detalhe.html'
    context_object_name = 'album'

    def get_queryset(self):
        return super().get_queryset().select_related('artista')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        musicas = self.object.musicas.filter(aprovado=True).select_related('album').prefetch_related('artistas')
        contexto['musicas'] = musicas
        contexto['duracao_total'] = sum(m.duracao for m in musicas)
        return contexto


class AlbumCreateView(CadastroComAprovacaoMixin, VoltarParaNextMixin, FormularioMixin, CreateView):
    model = Album
    form_class = AlbumForm
    titulo_pagina = 'Cadastrar álbum'
    campos_relacionados = ('artista',)
    url_apos_envio = reverse_lazy('musica:album_lista')
    success_message = 'Álbum "%(objeto)s" cadastrado com sucesso!'

    def get_initial(self):
        # Permite abrir o formulário já com o artista escolhido: ?artista=3
        inicial = super().get_initial()
        if self.request.GET.get('artista'):
            inicial['artista'] = self.request.GET['artista']
        return inicial


class AlbumUpdateView(GestorRequiredMixin, VoltarParaNextMixin, FormularioMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    titulo_pagina = 'Editar álbum'
    success_message = 'Álbum "%(objeto)s" atualizado com sucesso!'


class AlbumDeleteView(GestorRequiredMixin, VoltarParaNextMixin, ExclusaoMixin, DeleteView):
    model = Album
    tipo_objeto = 'o álbum'
    aviso_exclusao = 'Todas as músicas deste álbum também serão excluídas.'
    success_url = reverse_lazy('musica:album_lista')
    success_message = 'Álbum "%(objeto)s" excluído com sucesso!'
