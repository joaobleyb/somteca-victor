"""
Mixins reaproveitados pelas views de cadastro, edição e exclusão.

Um mixin é uma classe que "acrescenta" um comportamento a outra classe por
herança. Assim evitamos repetir o mesmo código em todas as views do CRUD.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin


class FormularioMixin(SuccessMessageMixin):
    """
    Usado nas CreateView e UpdateView.

    Todas usam o mesmo template genérico (compartilhado/form.html), que recebe
    o título da página e o texto do botão pelo contexto.
    """

    template_name = 'compartilhado/form.html'
    titulo_pagina = ''
    texto_botao = 'Salvar'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo_pagina'] = self.titulo_pagina
        contexto['texto_botao'] = self.texto_botao
        return contexto

    def get_success_message(self, cleaned_data):
        # Permite usar %(objeto)s na mensagem, com o nome do item salvo
        return self.success_message % {'objeto': self.object}


class ExclusaoMixin(SuccessMessageMixin):
    """Usado nas DeleteView: página de confirmação + mensagem de sucesso."""

    template_name = 'compartilhado/confirmar_exclusao.html'
    tipo_objeto = 'item'
    aviso_exclusao = ''  # ex.: avisar que os álbuns do artista também serão apagados

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['tipo_objeto'] = self.tipo_objeto
        contexto['aviso_exclusao'] = self.aviso_exclusao
        return contexto

    def get_success_message(self, cleaned_data):
        return self.success_message % {'objeto': self.object}


class VoltarParaNextMixin:
    """
    Se a URL (ou o formulário) trouxer ?next=/algum/lugar/, volta para lá depois
    de salvar/excluir. Usado pelo painel do gestor para retornar ao painel.
    Só aceita endereços do próprio site, por segurança.
    """

    def _url_next(self):
        from django.utils.http import url_has_allowed_host_and_scheme

        destino = self.request.POST.get('next') or self.request.GET.get('next')
        if destino and url_has_allowed_host_and_scheme(
            destino, allowed_hosts={self.request.get_host()}, require_https=self.request.is_secure(),
        ):
            return destino
        return None

    def get_success_url(self):
        return self._url_next() or super().get_success_url()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['url_next'] = self._url_next()
        return contexto


class GestorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Só usuários da equipe (is_staff) passam.
    - Não logado: vai para a página de login.
    - Logado, mas não é gestor: recebe 403 (acesso negado).
    """

    def test_func(self):
        return self.request.user.is_staff


class SoAprovadosMixin:
    """
    Nas páginas de detalhe, itens ainda não aprovados só abrem para o gestor
    (para os demais usuários respondem 404, como se não existissem).
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.aprovados()


class CadastroComAprovacaoMixin(LoginRequiredMixin):
    """
    Usado nas CreateView de artista, álbum e música.

    - Gestor: o cadastro já entra aprovado.
    - Demais usuários: o cadastro fica "aguardando aprovação" e só aparece no
      site depois que um gestor aprovar no painel. Nos campos de escolha
      (álbum, artista) eles só veem itens já aprovados.
    """

    # Campos do formulário que apontam para outros itens do catálogo
    campos_relacionados = ()
    url_apos_envio = None  # para onde vai quem não é gestor depois de enviar

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            for nome in self.campos_relacionados:
                campo = form.fields[nome]
                campo.queryset = campo.queryset.aprovados()
        return form

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['vai_para_aprovacao'] = not self.request.user.is_staff
        return contexto

    def form_valid(self, form):
        form.instance.enviado_por = self.request.user
        form.instance.aprovado = self.request.user.is_staff
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        if self.object.aprovado:
            return super().get_success_message(cleaned_data)
        return f'"{self.object}" foi enviado e está aguardando a aprovação de um gestor.'

    def get_success_url(self):
        if self.object.aprovado:
            return super().get_success_url()
        return str(self.url_apos_envio)
