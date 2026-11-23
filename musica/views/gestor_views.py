"""Painel do gestor: lista todas as músicas para adicionar, editar e remover."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from django.views.generic import ListView

from ..models import Album, Artista, Musica


class GestorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Só usuários da equipe (is_staff) entram no painel."""

    def test_func(self):
        return self.request.user.is_staff


class PainelGestorView(GestorRequiredMixin, ListView):
    model = Musica
    template_name = 'musica/gestor/painel.html'
    context_object_name = 'musicas'
    paginate_by = 20

    def get_queryset(self):
        musicas = (
            Musica.objects
            .select_related('album')
            .prefetch_related('artistas')
            .order_by('-data_criacao', 'titulo')
        )
        termo = self.request.GET.get('q', '').strip()
        if termo:
            musicas = musicas.filter(
                Q(titulo__icontains=termo)
                | Q(album__titulo__icontains=termo)
                | Q(artistas__nome__icontains=termo)
            ).distinct()
        return musicas

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['termo'] = self.request.GET.get('q', '').strip()
        contexto['total_musicas'] = Musica.objects.count()
        contexto['total_albuns'] = Album.objects.count()
        contexto['total_artistas'] = Artista.objects.count()
        contexto['total_reproducoes'] = Musica.objects.aggregate(t=Sum('total_reproducoes'))['t'] or 0
        return contexto
