"""
Comando de gerenciamento que enche o banco com dados de exemplo.

Uso:
    python manage.py popular_banco            # adiciona os dados de exemplo
    python manage.py popular_banco --limpar   # apaga o catálogo antes de popular

O que ele faz:
1. Cria usuários de teste (senha: somteca123).
2. Chama o comando `importar_musicas_reais`, que baixa 30 músicas reais de
   Kevin MacLeod (licença CC BY 4.0) e cadastra artista, coletâneas e faixas.
3. Monta playlists para os usuários com essas músicas.
4. Cria milhares de reproduções espalhadas pelos últimos ~14 meses, para
   testar as mais tocadas da semana.

Este arquivo também guarda a função `gerar_capa`, usada para desenhar as capas.
"""
import random
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from musica.models import Album, Artista, Musica, Reproducao
from playlists.models import Playlist

USUARIOS = [
    # (username, nome, senha)
    ('demo', 'Demo', 'somteca123'),
    ('ana', 'Ana', 'somteca123'),
    ('bruno', 'Bruno', 'somteca123'),
    ('carla', 'Carla', 'somteca123'),
]

# Playlists de exemplo: (nome, descrição, pública?, gêneros das músicas)
PLAYLISTS = [
    ('Para Estudar', 'Foco total para as provas do IFRS.', True, ['jazz', 'classica', 'eletronica']),
    ('Treino Pesado', 'Energia para a academia.', True, ['rock', 'eletronica', 'funk']),
    ('Bom Humor', 'Para começar o dia sorrindo.', True, ['pop', 'funk']),
    ('Só Minhas', 'Uma playlist privada de exemplo.', False, ['jazz', 'pop', 'classica']),
]

# Pares de cores (início, fim) do degradê das capas
CORES_CAPA = [
    ((29, 185, 84), (10, 60, 30)), ((255, 110, 199), (120, 20, 90)), ((255, 224, 102), (200, 110, 20)),
    ((79, 172, 254), (13, 60, 160)), ((179, 136, 255), (70, 40, 150)), ((255, 154, 90), (160, 50, 10)),
    ((80, 220, 200), (10, 90, 90)), ((240, 80, 80), (100, 10, 20)),
]


def gerar_capa(texto, cores):
    """Cria uma capa quadrada em degradê com o texto (usa o Pillow). Retorna bytes PNG."""
    from PIL import Image, ImageDraw, ImageFont

    tamanho = 400
    inicio, fim = cores
    imagem = Image.new('RGB', (tamanho, tamanho))
    desenho = ImageDraw.Draw(imagem)
    # Degradê vertical: desenha linhas horizontais com cores intermediárias
    for y in range(tamanho):
        t = y / tamanho
        cor = tuple(int(inicio[i] + (fim[i] - inicio[i]) * t) for i in range(3))
        desenho.line([(0, y), (tamanho, y)], fill=cor)

    try:
        fonte = ImageFont.load_default(size=36)
    except TypeError:  # versões antigas do Pillow não aceitam size
        fonte = ImageFont.load_default()

    # Quebra o título em linhas curtas
    linhas, linha = [], ''
    for palavra in texto.split():
        if len(linha) + len(palavra) > 12 and linha:
            linhas.append(linha)
            linha = palavra
        else:
            linha = f'{linha} {palavra}'.strip()
    linhas.append(linha)
    for i, conteudo in enumerate(linhas):
        desenho.text((28, 260 - (len(linhas) - 1 - i) * 44), conteudo, fill=(255, 255, 255), font=fonte)

    buffer = BytesIO()
    imagem.save(buffer, format='PNG')
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Cria usuários, baixa as 30 músicas reais e gera playlists e reproduções de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar', action='store_true',
            help='Apaga artistas, álbuns, músicas, playlists e reproduções antes de popular.',
        )
        parser.add_argument(
            '--reproducoes', type=int, default=4000,
            help='Quantidade de reproduções falsas a criar (padrão: 4000).',
        )

    def handle(self, *args, **opcoes):
        random.seed(42)  # resultados sempre iguais, bom para apresentações

        if opcoes['limpar']:
            self.stdout.write('Apagando dados antigos...')
            # O Django não apaga os arquivos de imagem ao excluir o registro,
            # então removemos as capas e fotos manualmente (os mp3 são mantidos
            # para não precisar baixar tudo de novo)
            for album in Album.objects.exclude(capa=''):
                album.capa.delete(save=False)
            for artista in Artista.objects.exclude(foto=''):
                artista.foto.delete(save=False)
            Reproducao.objects.all().delete()
            Playlist.objects.all().delete()
            Artista.objects.all().delete()  # em cascata apaga álbuns e músicas

        usuarios = self.criar_usuarios()

        # Baixa e cadastra as músicas reais (as reproduções são criadas aqui embaixo)
        call_command('importar_musicas_reais', reproducoes=0, stdout=self.stdout)
        musicas = list(Musica.objects.select_related('album'))

        self.criar_playlists(usuarios, musicas)
        self.criar_reproducoes(usuarios, musicas, opcoes['reproducoes'])

        self.stdout.write(self.style.SUCCESS(
            f'\nPronto! {len(musicas)} músicas, {Playlist.objects.count()} playlists e '
            f'{Reproducao.objects.count()} reproduções no banco.'
        ))
        self.stdout.write('Entre com o usuário "demo" e a senha "somteca123" para usar o painel do gestor.')

    # ------------------------------------------------------------------
    def criar_usuarios(self):
        usuarios = []
        for username, nome, senha in USUARIOS:
            usuario, criado = User.objects.get_or_create(
                username=username, defaults={'first_name': nome, 'email': f'{username}@exemplo.com'},
            )
            if criado:
                usuario.set_password(senha)
                usuario.save()
            usuarios.append(usuario)
        self.stdout.write(f'Usuários: {", ".join(u.username for u in usuarios)} (senha: somteca123)')
        return usuarios

    def criar_playlists(self, usuarios, musicas):
        """Cada usuário ganha 2 playlists sorteadas, com músicas dos gêneros da playlist."""
        for usuario in usuarios:
            for nome, descricao, publica, generos in random.sample(PLAYLISTS, 2):
                playlist, criada = Playlist.objects.get_or_create(
                    nome=nome, usuario=usuario, defaults={'descricao': descricao, 'publica': publica},
                )
                if criada:
                    candidatas = [m for m in musicas if m.album.genero in generos]
                    for musica in random.sample(candidatas, min(8, len(candidatas))):
                        playlist.adicionar_musica(musica)
        self.stdout.write(f'Playlists: {Playlist.objects.count()} no total.')

    def criar_reproducoes(self, usuarios, musicas, quantidade):
        """
        Cria reproduções falsas nos últimos ~14 meses. Cada usuário tem
        "músicas favoritas" com mais peso, para as mais tocadas da semana
        ficarem interessantes (e diferentes entre usuários).
        """
        if not quantidade or not musicas:
            return
        agora = timezone.now()
        pesos_por_usuario = {u.pk: [random.random() ** 3 for _ in musicas] for u in usuarios}
        donos = usuarios + [None]  # None = visitante não logado

        reproducoes = []
        for _ in range(quantidade):
            usuario = random.choice(donos)
            pesos = pesos_por_usuario[usuario.pk] if usuario else None
            musica = random.choices(musicas, weights=pesos)[0]
            # Mais reproduções recentes: sorteia "dias atrás" com viés para perto de hoje
            dias_atras = int(random.triangular(0, 420, 0))
            data_hora = agora - timedelta(days=dias_atras, minutes=random.randint(0, 1439))
            reproducoes.append(Reproducao(usuario=usuario, musica=musica, data_hora=data_hora))

        Reproducao.objects.bulk_create(reproducoes, batch_size=500)

        # Atualiza o contador total_reproducoes de cada música
        for musica in musicas:
            total = Reproducao.objects.filter(musica=musica).count()
            Musica.objects.filter(pk=musica.pk).update(total_reproducoes=total)

        self.stdout.write(f'Reproduções: {quantidade} criadas.')
