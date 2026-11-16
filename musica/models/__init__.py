"""
Models do app musica.

Cada model fica em seu próprio arquivo dentro desta pasta. Aqui importamos
todos para que o Django os encontre e para podermos escrever
`from musica.models import Musica` em qualquer lugar do projeto.
"""
from .artista import Artista
from .album import Album, GENEROS
from .musica import Musica
from .reproducao import Reproducao

__all__ = ['Artista', 'Album', 'GENEROS', 'Musica', 'Reproducao']
