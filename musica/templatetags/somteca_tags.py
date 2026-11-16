"""
Tags e filtros de template personalizados da SomTeca.

Uso nos templates: {% load somteca_tags %}
"""
from django import template
from django.utils.html import json_script

from musica.utils import musica_para_dict

register = template.Library()


@register.simple_tag
def fila_json(musicas, id_elemento):
    """
    Gera um <script type="application/json"> com a lista de músicas.

    O player (static/js/player.js) lê esse JSON para montar a fila de reprodução
    quando o usuário clica em um botão com data-fila="<id_elemento>".
    """
    faixas = [musica_para_dict(m) for m in musicas]
    return json_script(faixas, id_elemento)


@register.filter
def minutos(segundos):
    """Converte segundos em minutos inteiros (ex.: 3600 -> 60)."""
    return (segundos or 0) // 60


@register.filter
def duracao(segundos):
    """Formata segundos como mm:ss."""
    minutos_, seg = divmod(int(segundos or 0), 60)
    return f'{minutos_}:{seg:02d}'
