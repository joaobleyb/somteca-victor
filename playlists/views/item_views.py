"""
Views que alteram as músicas dentro de uma playlist
(adicionar, remover e mudar a ordem). Todas aceitam apenas POST.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from ..forms import AdicionarMusicaForm
from ..models import ItemPlaylist, Playlist


def _playlist_do_usuario(request, pk):
    """Busca a playlist garantindo que pertence ao usuário logado (senão, 404)."""
    return get_object_or_404(Playlist, pk=pk, usuario=request.user)


@login_required
@require_POST
def adicionar_musica(request, pk):
    playlist = _playlist_do_usuario(request, pk)
    form = AdicionarMusicaForm(request.POST, playlist=playlist)
    if form.is_valid():
        musica = form.cleaned_data['musica']
        playlist.adicionar_musica(musica)
        messages.success(request, f'"{musica}" adicionada à playlist!')
    else:
        messages.error(request, 'Escolha uma música válida para adicionar.')
    return redirect(playlist)


@login_required
@require_POST
def remover_item(request, pk, item_pk):
    playlist = _playlist_do_usuario(request, pk)
    item = get_object_or_404(ItemPlaylist, pk=item_pk, playlist=playlist)
    titulo = item.musica.titulo
    item.delete()
    playlist.reordenar()
    messages.success(request, f'"{titulo}" removida da playlist.')
    return redirect(playlist)


@login_required
@require_POST
def mover_item(request, pk, item_pk, direcao):
    """Troca a música de posição com a vizinha de cima ('subir') ou de baixo ('descer')."""
    if direcao not in ('subir', 'descer'):
        raise Http404('Direção inválida.')
    playlist = _playlist_do_usuario(request, pk)
    item = get_object_or_404(ItemPlaylist, pk=item_pk, playlist=playlist)

    if direcao == 'subir':
        vizinho = playlist.itens.filter(ordem__lt=item.ordem).order_by('-ordem').first()
    else:
        vizinho = playlist.itens.filter(ordem__gt=item.ordem).order_by('ordem').first()

    if vizinho:
        item.ordem, vizinho.ordem = vizinho.ordem, item.ordem
        item.save(update_fields=['ordem'])
        vizinho.save(update_fields=['ordem'])
    return redirect(playlist)
