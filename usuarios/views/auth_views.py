"""Cadastro, login e logout usando o django.contrib.auth."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..forms import CadastroForm, LoginForm


class CadastroView(CreateView):
    """Cria a conta e já faz o login do novo usuário."""
    form_class = CadastroForm
    template_name = 'usuarios/cadastro.html'
    success_url = reverse_lazy('musica:dashboard')

    def dispatch(self, request, *args, **kwargs):
        # Quem já está logado não precisa se cadastrar de novo
        if request.user.is_authenticated:
            return redirect('musica:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        resposta = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Conta criada! Bem-vindo(a) à SomTeca, {self.object.first_name}!')
        return resposta


class EntrarView(LoginView):
    """Login com o formulário estilizado e mensagem de boas-vindas."""
    form_class = LoginForm
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        resposta = super().form_valid(form)
        usuario = form.get_user()
        messages.success(self.request, f'Olá, {usuario.first_name or usuario.username}! Bom te ver de novo.')
        return resposta


class SairView(LogoutView):
    """Logout (no Django atual, o logout precisa ser feito via POST)."""

    def post(self, request, *args, **kwargs):
        messages.info(request, 'Você saiu da sua conta. Até logo!')
        return super().post(request, *args, **kwargs)
