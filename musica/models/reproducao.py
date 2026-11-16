from django.conf import settings
from django.db import models
from django.utils import timezone


class Reproducao(models.Model):
    """
    Registra cada vez que uma música é tocada no player.

    É a base do ranking de mais ouvidas e da retrospectiva do ano.
    """

    # Pode ser nulo para registrar reproduções de visitantes não logados
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reproducoes',
        null=True,
        blank=True,
        verbose_name='usuário',
    )
    musica = models.ForeignKey(
        'musica.Musica',
        on_delete=models.CASCADE,
        related_name='reproducoes',
        verbose_name='música',
    )
    # default=timezone.now (em vez de auto_now_add) permite que o comando
    # popular_banco crie reproduções com datas no passado
    data_hora = models.DateTimeField('data e hora', default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'reprodução'
        verbose_name_plural = 'reproduções'
        ordering = ['-data_hora']

    def __str__(self):
        quem = self.usuario or 'visitante'
        return f'{self.musica} — {quem} em {self.data_hora:%d/%m/%Y %H:%M}'
