"""Funções auxiliares usadas pelas views e templates do app musica."""
from datetime import timedelta

from django.utils import timezone

# Períodos aceitos pelo filtro do ranking: chave -> (rótulo, nº de dias ou None)
PERIODOS = {
    'semana': ('Última semana', 7),
    'mes': ('Último mês', 30),
    'sempre': ('Sempre', None),
}


def inicio_do_periodo(periodo):
    """Retorna a data/hora de início de um período, ou None para 'sempre'."""
    _, dias = PERIODOS.get(periodo, PERIODOS['semana'])
    if dias is None:
        return None
    return timezone.now() - timedelta(days=dias)


def musica_para_dict(musica):
    """
    Converte uma música em um dicionário simples, que é enviado ao player
    JavaScript (em formato JSON) com tudo o que ele precisa para tocar a faixa.
    """
    capa = musica.album.capa.url if musica.album.capa else ''
    return {
        'id': musica.pk,
        'titulo': musica.titulo,
        'artistas': musica.nomes_artistas,
        'album': musica.album.titulo,
        'capa': capa,
        'src': musica.arquivo_audio.url if musica.arquivo_audio else '',
        'url': musica.get_absolute_url(),
    }
