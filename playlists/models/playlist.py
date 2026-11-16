from django.conf import settings
from django.db import models, transaction
from django.db.models import Max
from django.urls import reverse


class Playlist(models.Model):
    """Uma lista de músicas criada por um usuário."""

    nome = models.CharField('nome', max_length=120)
    descricao = models.TextField('descrição', blank=True)
    capa = models.ImageField('capa', upload_to='playlists/', blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name='dono',
    )
    # ManyToMany com tabela intermediária: o model ItemPlaylist guarda,
    # além da música, a ordem dela na playlist e quando foi adicionada
    musicas = models.ManyToManyField(
        'musica.Musica',
        through='playlists.ItemPlaylist',
        related_name='playlists',
        verbose_name='músicas',
    )
    publica = models.BooleanField(
        'pública',
        default=True,
        help_text='Playlists públicas aparecem para todos; privadas só para você.',
    )
    data_criacao = models.DateTimeField('data de criação', auto_now_add=True)

    class Meta:
        verbose_name = 'playlist'
        verbose_name_plural = 'playlists'
        ordering = ['-data_criacao']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('playlists:detalhe', args=[self.pk])

    # ------------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------------
    def itens_ordenados(self):
        """Itens (posição + música) na ordem definida pelo usuário."""
        return (
            self.itens.order_by('ordem')
            .select_related('musica__album')
            .prefetch_related('musica__artistas')
        )

    def capa_url(self):
        """Usa a capa da playlist; se não tiver, a capa do álbum da 1ª música."""
        if self.capa:
            return self.capa.url
        primeiro = self.itens.select_related('musica__album').first()
        if primeiro and primeiro.musica.album.capa:
            return primeiro.musica.album.capa.url
        return ''

    def adicionar_musica(self, musica):
        """Adiciona uma música no fim da playlist. Retorna False se já estava nela."""
        if self.itens.filter(musica=musica).exists():
            return False
        ultima_ordem = self.itens.aggregate(maior=Max('ordem'))['maior'] or 0
        self.itens.create(musica=musica, ordem=ultima_ordem + 1)
        return True

    @transaction.atomic
    def definir_musicas(self, musicas):
        """
        Sincroniza a playlist com a lista de músicas escolhida no formulário:
        remove as que saíram, mantém a ordem das que ficaram e adiciona as novas no fim.
        """
        selecionadas = set(m.pk for m in musicas)
        self.itens.exclude(musica_id__in=selecionadas).delete()
        for musica in musicas:
            self.adicionar_musica(musica)
        self.reordenar()

    def reordenar(self):
        """Renumera as posições (1, 2, 3...) para não deixar buracos na ordem."""
        for posicao, item in enumerate(self.itens.order_by('ordem'), start=1):
            if item.ordem != posicao:
                item.ordem = posicao
                item.save(update_fields=['ordem'])

    @property
    def duracao_total(self):
        """Soma da duração das músicas, em segundos."""
        return self.musicas.aggregate(total=models.Sum('duracao'))['total'] or 0
