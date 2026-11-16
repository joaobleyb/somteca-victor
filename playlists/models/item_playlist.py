from django.db import models


class ItemPlaylist(models.Model):
    """
    Tabela intermediária entre Playlist e Musica.

    Cada linha representa "a música X está na posição N da playlist Y".
    """

    playlist = models.ForeignKey(
        'playlists.Playlist',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='playlist',
    )
    musica = models.ForeignKey(
        'musica.Musica',
        on_delete=models.CASCADE,
        verbose_name='música',
    )
    ordem = models.PositiveIntegerField('ordem', default=1)
    adicionada_em = models.DateTimeField('adicionada em', auto_now_add=True)

    class Meta:
        verbose_name = 'item da playlist'
        verbose_name_plural = 'itens da playlist'
        ordering = ['ordem']
        constraints = [
            # A mesma música não pode aparecer duas vezes na mesma playlist
            models.UniqueConstraint(fields=['playlist', 'musica'], name='musica_unica_por_playlist'),
        ]

    def __str__(self):
        return f'{self.ordem}. {self.musica} ({self.playlist})'
