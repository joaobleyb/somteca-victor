"""Busca geral em músicas, artistas e álbuns."""
from django.db.models import Q
from django.views.generic import TemplateView

from ..models import Album, Artista, Musica


class BuscaView(TemplateView):
    """
    Procura o termo digitado (?q=...) nos três models ao mesmo tempo.

    Os objetos Q permitem combinar condições com OU ( | ), por exemplo:
    "título contém o termo OU nome do artista contém o termo".
    """
    template_name = 'musica/busca.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        termo = self.request.GET.get('q', '').strip()
        contexto['termo'] = termo

        if termo:
            contexto['musicas'] = (
                Musica.objects.aprovados()
                .filter(
                    Q(titulo__icontains=termo)
                    | Q(artistas__nome__icontains=termo)
                    | Q(album__titulo__icontains=termo)
                )
                .select_related('album')
                .prefetch_related('artistas')
                .distinct()  # evita repetir músicas que casam por mais de um artista
            )
            contexto['artistas'] = Artista.objects.aprovados().filter(
                Q(nome__icontains=termo) | Q(pais_origem__icontains=termo)
            )
            contexto['albuns'] = (
                Album.objects.aprovados()
                .filter(Q(titulo__icontains=termo) | Q(artista__nome__icontains=termo))
                .select_related('artista')
            )
            contexto['total'] = (
                len(contexto['musicas']) + len(contexto['artistas']) + len(contexto['albuns'])
            )
        return contexto
