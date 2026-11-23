"""Funções auxiliares usadas pelas views e templates do app musica."""


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
