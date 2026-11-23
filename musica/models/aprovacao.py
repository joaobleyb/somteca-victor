"""
Campos e consultas de aprovação usados por Artista, Album e Musica.

Cadastros feitos por quem não é gestor ficam com aprovado=False e só
aparecem no site depois que um gestor aprova no painel.
"""
from django.conf import settings
from django.db import models


class AprovacaoMixin(models.Model):
    """Model abstrato: acrescenta os campos de aprovação a quem herdar dele."""

    # default=True: itens criados pelo admin e pelos comandos já entram aprovados.
    # As telas do site definem False quando quem cadastra não é gestor.
    aprovado = models.BooleanField('aprovado', default=True)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='enviado por',
    )

    class Meta:
        abstract = True


class ArtistaQuerySet(models.QuerySet):
    def aprovados(self):
        return self.filter(aprovado=True)


class AlbumQuerySet(models.QuerySet):
    def aprovados(self):
        # Um álbum só aparece se ele e o artista dele estiverem aprovados
        return self.filter(aprovado=True, artista__aprovado=True)


class MusicaQuerySet(models.QuerySet):
    def aprovados(self):
        return self.filter(aprovado=True, album__aprovado=True, album__artista__aprovado=True)
