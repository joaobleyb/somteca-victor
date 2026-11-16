from django.db import models
from django.urls import reverse


class Artista(models.Model):
    """Um artista ou banda cadastrado na biblioteca."""

    nome = models.CharField('nome', max_length=150, unique=True)
    biografia = models.TextField('biografia', blank=True)
    foto = models.ImageField('foto', upload_to='artistas/', blank=True)
    pais_origem = models.CharField('país de origem', max_length=80)
    data_criacao = models.DateTimeField('data de criação', auto_now_add=True)

    class Meta:
        verbose_name = 'artista'
        verbose_name_plural = 'artistas'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        """URL da página de detalhes (usada após cadastrar/editar)."""
        return reverse('musica:artista_detalhe', args=[self.pk])
