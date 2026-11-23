"""Painel do gestor: aprovação de cadastros e gestão das músicas."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from ..models import Album, Artista, Musica
from .mixins import GestorRequiredMixin

# Tipos de item que podem ser aprovados: nome na URL -> (model, nome para mensagens)
TIPOS_APROVACAO = {
    'artista': (Artista, 'Artista'),
    'album': (Album, 'Álbum'),
    'musica': (Musica, 'Música'),
}


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
            .order_by('aprovado', '-data_criacao', 'titulo')  # pendentes primeiro
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

        # Cadastros aguardando aprovação (com quem enviou)
        contexto['pendentes_artistas'] = Artista.objects.filter(aprovado=False).select_related('enviado_por')
        contexto['pendentes_albuns'] = Album.objects.filter(aprovado=False).select_related('artista', 'enviado_por')
        contexto['pendentes_musicas'] = (
            Musica.objects.filter(aprovado=False).select_related('album__artista', 'enviado_por')
        )
        contexto['total_pendentes'] = (
            len(contexto['pendentes_artistas']) + len(contexto['pendentes_albuns'])
            + len(contexto['pendentes_musicas'])
        )

        # Contadores do que já está publicado no site
        contexto['total_musicas'] = Musica.objects.aprovados().count()
        contexto['total_albuns'] = Album.objects.aprovados().count()
        contexto['total_artistas'] = Artista.objects.aprovados().count()
        contexto['total_reproducoes'] = Musica.objects.aggregate(t=Sum('total_reproducoes'))['t'] or 0
        return contexto


@staff_member_required
@require_POST
def aprovar(request, tipo, pk):
    """Aprova um artista, álbum ou música enviado por um usuário (só gestor, só POST)."""
    if tipo not in TIPOS_APROVACAO:
        raise Http404('Tipo inválido.')
    model, nome = TIPOS_APROVACAO[tipo]
    item = get_object_or_404(model, pk=pk)
    item.aprovado = True
    item.save(update_fields=['aprovado'])
    messages.success(request, f'{nome} "{item}" aprovado(a) e publicado(a) no site!')

    destino = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        destino = 'musica:gestor'
    return redirect(destino)
