from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Musica(models.Model):
    """Uma faixa de um álbum, com o arquivo de áudio em .mp3."""

    titulo = models.CharField('título', max_length=150)
    album = models.ForeignKey(
        'musica.Album',
        on_delete=models.CASCADE,
        related_name='musicas',
        verbose_name='álbum',
    )
    # ManyToMany: uma música pode ter vários artistas (participações / "feat.")
    artistas = models.ManyToManyField(
        'musica.Artista',
        related_name='musicas',
        verbose_name='artistas',
    )
    # Só aceita arquivos com extensão .mp3
    arquivo_audio = models.FileField(
        'arquivo de áudio (.mp3)',
        upload_to='musicas/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3'])],
    )
    # A duração é guardada em segundos (ex.: 215 = 3:35)
    duracao = models.PositiveIntegerField(
        'duração (segundos)',
        validators=[MinValueValidator(1)],
    )
    numero_faixa = models.PositiveSmallIntegerField(
        'número da faixa',
        validators=[MinValueValidator(1)],
    )
    # Contador geral de reproduções (atualizado pelo player a cada play)
    total_reproducoes = models.PositiveIntegerField('reproduções', default=0)
    data_criacao = models.DateTimeField('data de criação', auto_now_add=True)

    class Meta:
        verbose_name = 'música'
        verbose_name_plural = 'músicas'
        ordering = ['album', 'numero_faixa']
        constraints = [
            # Não pode haver duas faixas com o mesmo número no mesmo álbum
            models.UniqueConstraint(
                fields=['album', 'numero_faixa'],
                name='faixa_unica_por_album',
                violation_error_message='Já existe uma faixa com esse número neste álbum.',
            ),
        ]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('musica:musica_detalhe', args=[self.pk])

    @property
    def duracao_formatada(self):
        """Retorna a duração no formato mm:ss (ex.: 3:35)."""
        minutos, segundos = divmod(self.duracao or 0, 60)
        return f'{minutos}:{segundos:02d}'

    @property
    def genero(self):
        """O gênero da música é o gênero do álbum ao qual ela pertence."""
        return self.album.get_genero_display()

    @property
    def nomes_artistas(self):
        """Nomes dos artistas separados por vírgula (ex.: 'Fulano, Ciclano')."""
        return ', '.join(artista.nome for artista in self.artistas.all())
