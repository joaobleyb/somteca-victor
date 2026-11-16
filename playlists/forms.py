"""Formulários do app playlists."""
from django import forms

from musica.forms import BootstrapFormMixin
from musica.models import Musica

from .models import Playlist


class PlaylistForm(BootstrapFormMixin, forms.ModelForm):
    """
    Formulário de playlist.

    O campo `musicas` não é o ManyToMany do model (que usa tabela intermediária
    e não pode ser salvo direto pelo ModelForm). Ele é um campo extra; depois de
    salvar, a view chama playlist.definir_musicas() para criar os ItemPlaylist.
    """

    musicas = forms.ModelMultipleChoiceField(
        label='Músicas',
        queryset=Musica.objects.select_related('album').order_by('titulo'),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10}),
        help_text='Segure Ctrl (ou Cmd) para escolher várias. Você também pode '
                  'adicionar e reordenar músicas na página da playlist.',
    )

    class Meta:
        model = Playlist
        fields = ['nome', 'descricao', 'capa', 'publica']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'capa': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na edição, já deixa marcadas as músicas que estão na playlist
        if self.instance.pk:
            self.initial['musicas'] = list(self.instance.musicas.values_list('pk', flat=True))
        # Mostra "Música — Álbum" nas opções, para diferenciar títulos iguais
        self.fields['musicas'].label_from_instance = lambda m: f'{m.titulo} — {m.album.titulo}'


class AdicionarMusicaForm(BootstrapFormMixin, forms.Form):
    """Formulário pequeno da página da playlist para incluir uma música."""

    musica = forms.ModelChoiceField(
        label='Adicionar música',
        queryset=Musica.objects.select_related('album').order_by('titulo'),
        empty_label='Escolha uma música...',
    )

    def __init__(self, *args, playlist=None, **kwargs):
        super().__init__(*args, **kwargs)
        if playlist is not None:
            # Não oferece músicas que já estão na playlist
            self.fields['musica'].queryset = self.fields['musica'].queryset.exclude(
                pk__in=playlist.musicas.values('pk')
            )
        self.fields['musica'].label_from_instance = lambda m: f'{m.titulo} — {m.album.titulo}'
