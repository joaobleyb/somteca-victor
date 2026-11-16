"""Formulários (ModelForms) do catálogo musical."""
import re

from django import forms

from .models import Album, Artista, Musica


class BootstrapFormMixin:
    """
    Adiciona automaticamente as classes CSS do Bootstrap aos campos do formulário,
    para não precisar configurar widget por widget.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                classe = 'form-check-input'
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                classe = ''  # cada opção é estilizada no template
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                classe = 'form-select'
            else:
                classe = 'form-control'
            if classe:
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} {classe}".strip()


class ArtistaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Artista
        fields = ['nome', 'pais_origem', 'biografia', 'foto']
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
            'foto': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }


class AlbumForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Album
        fields = ['titulo', 'artista', 'ano_lancamento', 'genero', 'capa']
        widgets = {
            'capa': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }


class MusicaForm(BootstrapFormMixin, forms.ModelForm):
    """
    Formulário de música.

    A duração é digitada no formato "mm:ss" (mais natural para o usuário)
    e convertida para segundos antes de ser salva no banco.
    """

    duracao = forms.CharField(
        label='Duração (mm:ss)',
        max_length=8,
        widget=forms.TextInput(attrs={'placeholder': 'ex.: 3:45'}),
    )

    class Meta:
        model = Musica
        fields = ['titulo', 'album', 'artistas', 'numero_faixa', 'duracao', 'arquivo_audio']
        widgets = {
            'artistas': forms.SelectMultiple(attrs={'size': 6}),
            'arquivo_audio': forms.ClearableFileInput(attrs={'accept': '.mp3,audio/mpeg'}),
        }
        help_texts = {
            'artistas': 'Segure Ctrl (ou Cmd) para selecionar mais de um artista (participações).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na edição, mostra a duração já salva no formato mm:ss
        if self.instance.pk and self.instance.duracao:
            self.initial['duracao'] = self.instance.duracao_formatada

    def clean_duracao(self):
        """Converte "mm:ss" (ou só segundos) para um número inteiro de segundos."""
        valor = self.cleaned_data['duracao'].strip()
        if re.fullmatch(r'\d+', valor):
            segundos = int(valor)
        elif re.fullmatch(r'\d+:[0-5]\d', valor):
            minutos, seg = valor.split(':')
            segundos = int(minutos) * 60 + int(seg)
        else:
            raise forms.ValidationError('Use o formato mm:ss, por exemplo 3:45.')
        if segundos <= 0:
            raise forms.ValidationError('A duração deve ser maior que zero.')
        return segundos

    def clean(self):
        """Garante que o artista dono do álbum esteja entre os artistas da música."""
        dados = super().clean()
        album = dados.get('album')
        artistas = dados.get('artistas')
        if album and artistas is not None and album.artista not in artistas:
            self.add_error(
                'artistas',
                f'O artista do álbum ({album.artista}) precisa estar entre os artistas da música.',
            )
        return dados
