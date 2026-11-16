"""Retrospectiva do ano (no estilo "Wrapped") do usuário logado."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from django.views.generic import TemplateView

from musica.models import GENEROS, Artista, Musica, Reproducao

MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
MESES_EXTENSO = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
]


class RetrospectivaView(LoginRequiredMixin, TemplateView):
    """
    Resume tudo o que o usuário ouviu em um ano (o atual, ou ?ano=2025).

    Todos os números saem da tabela Reproducao, filtrada pelo usuário e pelo ano.
    """
    template_name = 'usuarios/retrospectiva.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Anos em que o usuário tem reproduções (para o seletor de ano)
        anos_disponiveis = sorted(
            {data.year for data in Reproducao.objects.filter(usuario=usuario).dates('data_hora', 'year')},
            reverse=True,
        )
        ano_atual = timezone.localdate().year
        ano = self.request.GET.get('ano', '')
        ano = int(ano) if ano.isdigit() else ano_atual

        # Todas as reproduções do usuário no ano escolhido
        reproducoes = Reproducao.objects.filter(usuario=usuario, data_hora__year=ano)

        # 1) Total de minutos ouvidos (soma da duração de cada música tocada)
        segundos = reproducoes.aggregate(total=Sum('musica__duracao'))['total'] or 0

        # Filtro reaproveitado nos tops: "reproduções deste usuário neste ano"
        def filtro(caminho):
            return Q(**{f'{caminho}__usuario': usuario, f'{caminho}__data_hora__year': ano})

        # 2) Top 5 músicas e top 5 artistas
        top_musicas = (
            Musica.objects.select_related('album').prefetch_related('artistas')
            .annotate(plays=Count('reproducoes', filter=filtro('reproducoes')))
            .filter(plays__gt=0)
            .order_by('-plays', 'titulo')[:5]
        )
        top_artistas = (
            Artista.objects
            .annotate(plays=Count('musicas__reproducoes', filter=filtro('musicas__reproducoes')))
            .filter(plays__gt=0)
            .order_by('-plays', 'nome')[:5]
        )

        # 3) Gênero favorito: agrupa as reproduções pelo gênero do álbum
        genero = (
            reproducoes.values('musica__album__genero')
            .annotate(total=Count('id'))
            .order_by('-total')
            .first()
        )
        nomes_generos = dict(GENEROS)
        genero_favorito = nomes_generos.get(genero['musica__album__genero']) if genero else None

        # 4) Minutos ouvidos em cada mês (para o gráfico de linha)
        por_mes = (
            reproducoes.annotate(mes=ExtractMonth('data_hora'))
            .values('mes')
            .annotate(segundos=Sum('musica__duracao'))
        )
        minutos_por_mes = [0] * 12
        for linha in por_mes:
            minutos_por_mes[linha['mes'] - 1] = round((linha['segundos'] or 0) / 60)

        mes_top = None
        if any(minutos_por_mes):
            indice = minutos_por_mes.index(max(minutos_por_mes))
            mes_top = {'nome': MESES_EXTENSO[indice], 'minutos': minutos_por_mes[indice]}

        contexto.update({
            'ano': ano,
            'anos_disponiveis': anos_disponiveis or [ano_atual],
            'total_reproducoes': reproducoes.count(),
            'total_minutos': segundos // 60,
            'top_musicas': top_musicas,
            'top_artistas': top_artistas,
            'genero_favorito': genero_favorito,
            'mes_top': mes_top,
            'grafico_meses': {'rotulos': MESES, 'valores': minutos_por_mes},
        })
        return contexto
