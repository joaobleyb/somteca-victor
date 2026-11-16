"""CRUD de artistas usando Class-Based Views."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ..forms import ArtistaForm
from ..models import Artista
from .mixins import ExclusaoMixin, FormularioMixin


class ArtistaListView(ListView):
    """Lista todos os artistas em cards, 12 por página."""
    model = Artista
    template_name = 'musica/artista/lista.html'
    context_object_name = 'artistas'
    paginate_by = settings.ITENS_POR_PAGINA

    def get_queryset(self):
        # annotate adiciona a quantidade de álbuns em cada artista com uma só consulta
        # (com annotate o Django ignora o ordering do Meta, então ordenamos de novo)
        return Artista.objects.annotate(qtd_albuns=Count('albuns')).order_by('nome')


class ArtistaDetailView(DetailView):
    """Página do artista: biografia, álbuns e músicas em que participa."""
    model = Artista
    template_name = 'musica/artista/detalhe.html'
    context_object_name = 'artista'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['albuns'] = self.object.albuns.all()
        contexto['musicas'] = (
            self.object.musicas
            .select_related('album')
            .prefetch_related('artistas')
            .order_by('-total_reproducoes')
        )
        return contexto


class ArtistaCreateView(LoginRequiredMixin, FormularioMixin, CreateView):
    model = Artista
    form_class = ArtistaForm
    titulo_pagina = 'Cadastrar artista'
    success_message = 'Artista "%(objeto)s" cadastrado com sucesso!'


class ArtistaUpdateView(LoginRequiredMixin, FormularioMixin, UpdateView):
    model = Artista
    form_class = ArtistaForm
    titulo_pagina = 'Editar artista'
    success_message = 'Artista "%(objeto)s" atualizado com sucesso!'


class ArtistaDeleteView(LoginRequiredMixin, ExclusaoMixin, DeleteView):
    model = Artista
    tipo_objeto = 'o artista'
    aviso_exclusao = 'Os álbuns deste artista (e as músicas deles) também serão excluídos.'
    success_url = reverse_lazy('musica:artista_lista')
    success_message = 'Artista "%(objeto)s" excluído com sucesso!'
