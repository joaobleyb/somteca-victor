"""View chamada pelo player JavaScript a cada música tocada."""
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..models import Musica, Reproducao


@require_POST
def registrar_reproducao(request, pk):
    """
    Registra uma reprodução da música `pk`.

    É chamada via fetch() (POST com o token CSRF) pelo arquivo static/js/player.js.
    Responde em JSON para o JavaScript saber que deu certo.
    """
    musica = get_object_or_404(Musica.objects.aprovados(), pk=pk)

    # Visitantes não logados também contam nas mais tocadas (usuario fica vazio)
    usuario = request.user if request.user.is_authenticated else None
    Reproducao.objects.create(usuario=usuario, musica=musica)

    # F() faz o incremento direto no banco, evitando problemas se duas
    # pessoas tocarem a mesma música ao mesmo tempo
    Musica.objects.filter(pk=pk).update(total_reproducoes=F('total_reproducoes') + 1)
    musica.refresh_from_db(fields=['total_reproducoes'])

    return JsonResponse({'ok': True, 'musica': musica.pk, 'total': musica.total_reproducoes})
