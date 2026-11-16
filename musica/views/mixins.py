"""
Mixins reaproveitados pelas views de cadastro, edição e exclusão.

Um mixin é uma classe que "acrescenta" um comportamento a outra classe por
herança. Assim evitamos repetir o mesmo código em todas as views do CRUD.
"""
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
