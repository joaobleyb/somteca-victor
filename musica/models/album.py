from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

# Lista de gêneros musicais disponíveis (valor salvo no banco, texto exibido)
GENEROS = [
    ('rock', 'Rock'),
    ('pop', 'Pop'),
    ('mpb', 'MPB'),
    ('samba', 'Samba'),
    ('sertanejo', 'Sertanejo'),
    ('funk', 'Funk'),
    ('rap', 'Rap / Hip-Hop'),
    ('eletronica', 'Eletrônica'),
    ('jazz', 'Jazz'),
    ('classica', 'Clássica'),
    ('reggae', 'Reggae'),
    ('indie', 'Indie'),
    ('outro', 'Outro'),
]


class Album(models.Model):
    """Um álbum pertence a um artista principal e contém várias músicas."""

    titulo = models.CharField('título', max_length=150)
    # on_delete=CASCADE: ao excluir o artista, os álbuns dele também são excluídos
    artista = models.ForeignKey(
        'musica.Artista',
        on_delete=models.CASCADE,
        related_name='albuns',
        verbose_name='artista',
    )
    ano_lancamento = models.PositiveSmallIntegerField(
        'ano de lançamento',
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
    )
    capa = models.ImageField('capa', upload_to='capas/', blank=True)
    genero = models.CharField('gênero', max_length=20, choices=GENEROS)
    data_criacao = models.DateTimeField('data de criação', auto_now_add=True)

    class Meta:
        verbose_name = 'álbum'
        verbose_name_plural = 'álbuns'
        ordering = ['-ano_lancamento', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.ano_lancamento})'

    def get_absolute_url(self):
        return reverse('musica:album_detalhe', args=[self.pk])
