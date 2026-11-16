"""Página inicial (dashboard) da SomTeca."""
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from playlists.models import Playlist

from ..models import Album, Artista, Musica


class DashboardView(TemplateView):
    """Mostra contadores gerais, músicas recentes e as mais tocadas da semana."""
    template_name = 'musica/dashboard.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        # Saudação de acordo com a hora local
        hora = timezone.localtime().hour
        contexto['saudacao'] = 'Bom dia' if hora < 12 else 'Boa tarde' if hora < 18 else 'Boa noite'

        # Contadores gerais
        contexto['total_musicas'] = Musica.objects.count()
        contexto['total_artistas'] = Artista.objects.count()
        contexto['total_albuns'] = Album.objects.count()
        contexto['total_playlists'] = Playlist.objects.count()

        musicas = Musica.objects.select_related('album').prefetch_related('artistas')

        # As 8 músicas cadastradas mais recentemente
        contexto['recentes'] = musicas.order_by('-data_criacao')[:8]

        # As 5 mais tocadas nos últimos 7 dias (conta só as reproduções da semana)
        uma_semana_atras = timezone.now() - timedelta(days=7)
        contexto['top_semana'] = (
            musicas
            .annotate(plays=Count('reproducoes', filter=Q(reproducoes__data_hora__gte=uma_semana_atras)))
            .filter(plays__gt=0)
            .order_by('-plays')[:5]
        )
        return contexto
