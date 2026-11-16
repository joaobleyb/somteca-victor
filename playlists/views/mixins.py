"""Mixins de permissão do app playlists."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class DonoPlaylistMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Só deixa passar o usuário dono da playlist.

    - Não logado: é redirecionado para a página de login (LoginRequiredMixin).
    - Logado, mas não é o dono: recebe erro 403 - acesso negado (UserPassesTestMixin).
    """

    def test_func(self):
        return self.get_object().usuario == self.request.user
