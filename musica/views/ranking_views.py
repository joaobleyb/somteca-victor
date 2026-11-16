"""Ranking das músicas, artistas e álbuns mais ouvidos."""
from django.db.models import Count, Q
from django.views.generic import TemplateView

from ..models import Album, Artista, Musica
from ..utils import PERIODOS, inicio_do_periodo


def contar_reproducoes(caminho, inicio):
    """
    Monta um Count() das reproduções, opcionalmente filtrado por data.

    `caminho` é o caminho da relação até Reproducao a partir do model:
      - Musica  -> 'reproducoes'
      - Artista -> 'musicas__reproducoes'
      - Album   -> 'musicas__reproducoes'
    """
    if inicio is None:
        return Count(caminho)
    return Count(caminho, filter=Q(**{f'{caminho}__data_hora__gte': inicio}))


class RankingView(TemplateView):
    """Top 10 de músicas, artistas e álbuns, com filtro por período e gráficos."""
    template_name = 'musica/ranking.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        periodo = self.request.GET.get('periodo', 'semana')
        if periodo not in PERIODOS:
            periodo = 'semana'
        inicio = inicio_do_periodo(periodo)

        top_musicas = list(
            Musica.objects.select_related('album').prefetch_related('artistas')
            .annotate(plays=contar_reproducoes('reproducoes', inicio))
            .filter(plays__gt=0)
            .order_by('-plays', 'titulo')[:10]
        )
        top_artistas = list(
            Artista.objects
            .annotate(plays=contar_reproducoes('musicas__reproducoes', inicio))
            .filter(plays__gt=0)
            .order_by('-plays', 'nome')[:10]
        )
        top_albuns = list(
            Album.objects.select_related('artista')
            .annotate(plays=contar_reproducoes('musicas__reproducoes', inicio))
            .filter(plays__gt=0)
            .order_by('-plays', 'titulo')[:10]
        )

        contexto.update({
            'periodos': PERIODOS,
            'periodo': periodo,
            'top_musicas': top_musicas,
            'top_artistas': top_artistas,
            'top_albuns': top_albuns,
            # Dados para os gráficos (Chart.js), convertidos em JSON no template
            'grafico': {
                'musicas': {
                    'rotulos': [m.titulo for m in top_musicas],
                    'valores': [m.plays for m in top_musicas],
                },
                'artistas': {
                    'rotulos': [a.nome for a in top_artistas],
                    'valores': [a.plays for a in top_artistas],
                },
                'albuns': {
                    'rotulos': [a.titulo for a in top_albuns],
                    'valores': [a.plays for a in top_albuns],
                },
            },
        })
        return contexto
