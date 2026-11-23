"""Variáveis disponíveis em todos os templates."""
from .models import Album, Artista, Musica


def pendencias_gestor(request):
    """Quantidade de cadastros aguardando aprovação (só calculada para gestores)."""
    usuario = getattr(request, 'user', None)
    if not (usuario and usuario.is_staff):
        return {}
    total = (
        Artista.objects.filter(aprovado=False).count()
        + Album.objects.filter(aprovado=False).count()
        + Musica.objects.filter(aprovado=False).count()
    )
    return {'pendencias_gestor': total}
