"""CRUD de playlists."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from musica.views.mixins import ExclusaoMixin, FormularioMixin

from ..forms import AdicionarMusicaForm, PlaylistForm
from ..models import Playlist
from .mixins import DonoPlaylistMixin


def playlists_visiveis(usuario):
    """Playlists públicas de todos + as privadas do próprio usuário logado."""
    filtro = Q(publica=True)
    if usuario.is_authenticated:
        filtro |= Q(usuario=usuario)
    return Playlist.objects.filter(filtro)


class PlaylistListView(ListView):
    """Lista as playlists. Com ?minhas=1 mostra só as do usuário logado."""
    model = Playlist
    template_name = 'playlists/lista.html'
    context_object_name = 'playlists'
    paginate_by = settings.ITENS_POR_PAGINA

    def get_queryset(self):
        playlists = playlists_visiveis(self.request.user)
        if self.request.GET.get('minhas') and self.request.user.is_authenticated:
            playlists = playlists.filter(usuario=self.request.user)
        return (
            playlists.select_related('usuario')
            .annotate(qtd_musicas=Count('itens'))
            .order_by('-data_criacao')  # annotate descarta o ordering do Meta
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['so_minhas'] = bool(self.request.GET.get('minhas'))
        return contexto


class PlaylistDetailView(DetailView):
    """Página da playlist. Playlists privadas só abrem para o dono (senão, 404)."""
    model = Playlist
    template_name = 'playlists/detalhe.html'
    context_object_name = 'playlist'

    def get_queryset(self):
        return playlists_visiveis(self.request.user).select_related('usuario')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        itens = list(self.object.itens_ordenados())
        contexto['itens'] = itens
        contexto['musicas'] = [item.musica for item in itens]
        contexto['duracao_total'] = sum(item.musica.duracao for item in itens)
        contexto['eh_dono'] = self.object.usuario == self.request.user
        if contexto['eh_dono']:
            contexto['form_adicionar'] = AdicionarMusicaForm(playlist=self.object)
        return contexto


class PlaylistCreateView(LoginRequiredMixin, FormularioMixin, CreateView):
    model = Playlist
    form_class = PlaylistForm
    titulo_pagina = 'Criar playlist'
    success_message = 'Playlist "%(objeto)s" criada com sucesso!'

    def form_valid(self, form):
        # O dono é sempre o usuário logado (não aparece no formulário)
        form.instance.usuario = self.request.user
        resposta = super().form_valid(form)
        self.object.definir_musicas(form.cleaned_data['musicas'])
        return resposta


class PlaylistUpdateView(DonoPlaylistMixin, FormularioMixin, UpdateView):
    model = Playlist
    form_class = PlaylistForm
    titulo_pagina = 'Editar playlist'
    success_message = 'Playlist "%(objeto)s" atualizada com sucesso!'

    def form_valid(self, form):
        resposta = super().form_valid(form)
        self.object.definir_musicas(form.cleaned_data['musicas'])
        return resposta


class PlaylistDeleteView(DonoPlaylistMixin, ExclusaoMixin, DeleteView):
    model = Playlist
    tipo_objeto = 'a playlist'
    success_url = reverse_lazy('playlists:lista')
    success_message = 'Playlist "%(objeto)s" excluída com sucesso!'
