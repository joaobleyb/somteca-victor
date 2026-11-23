"""
Baixa 30 músicas reais com licença livre e cadastra no banco.

Uso:
    python manage.py importar_musicas_reais
    python manage.py importar_musicas_reais --reproducoes 0   # sem plays falsos

As faixas são do compositor Kevin MacLeod (incompetech.com), distribuídas sob a
licença Creative Commons Atribuição 4.0 (CC BY 4.0): podem ser usadas
livremente, desde que o autor seja creditado. Os créditos ficam na biografia
do artista e no README.

Os arquivos .mp3 vão para media/musicas/kevin-macleod/ (essa pasta não vai
para o Git, por isso existe este comando: quem clonar o projeto roda e baixa).
"""
import random
import struct
import urllib.parse
import urllib.request
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify

from musica.models import Album, Artista, Musica, Reproducao
from playlists.models import Playlist

from .popular_banco import CORES_CAPA, gerar_capa

URL_BASE = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/'
PASTA_DESTINO = 'musicas/kevin-macleod'

ARTISTA = {
    'nome': 'Kevin MacLeod',
    'pais': 'Estados Unidos',
    'bio': (
        'Compositor norte-americano conhecido por disponibilizar milhares de músicas '
        'gratuitamente em incompetech.com, usadas em vídeos, jogos e filmes no mundo todo.\n\n'
        'Créditos: todas as faixas deste artista são de Kevin MacLeod (incompetech.com), '
        'licenciadas sob Creative Commons: By Attribution 4.0 — '
        'https://creativecommons.org/licenses/by/4.0/'
    ),
}

# Coletâneas criadas para a SomTeca: (título, gênero, [nome do arquivo no incompetech])
COLETANEAS = [
    ('Lounge & Jazz', 'jazz', [
        'Airport Lounge', 'Backbay Lounge', 'Bossa Antigua', 'Night on the Docks - Sax', 'Smooth Lovin',
    ]),
    ('Diversão Garantida', 'pop', [
        'Monkeys Spinning Monkeys', 'Fluffing a Duck', 'Sneaky Snitch', 'Scheming Weasel faster',
        'Pixel Peeker Polka - faster', 'Spazzmatica Polka', 'Life of Riley',
    ]),
    ('Pixels & Sintetizadores', 'eletronica', [
        'Itty Bitty 8 Bit', 'Hyperfun', 'Blip Stream', 'Chill Wave', 'Aitech', 'Ouroboros',
    ]),
    ('Groove', 'funk', [
        'Funkorama', 'Groove Grove', 'Cool Vibes', 'Rollin at 5', 'Easy Lemon',
    ]),
    ('Adrenalina', 'rock', [
        'Killers', 'Volatile Reaction', 'Cut and Run', 'Furious Freak', 'Hitman',
    ]),
    ('Clássicos Revisitados', 'classica', [
        'Gymnopedie No 1', 'Danse Macabre',
    ]),
]

# Tabelas do formato MP3 (MPEG-1 Layer III) para calcular a duração
BITRATES_KBPS = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
TAXAS_AMOSTRAGEM = [44100, 48000, 32000, 0]


def duracao_mp3(dados):
    """
    Calcula a duração (em segundos) de um MP3 lendo os cabeçalhos do arquivo,
    sem precisar de biblioteca externa.

    1. Pula a tag ID3v2 (metadados no começo do arquivo), se houver.
    2. Acha o primeiro frame de áudio e lê o bitrate e a taxa de amostragem.
    3. Se o frame tiver o cabeçalho "Xing"/"Info" (MP3 VBR), usa o número de
       frames informado; senão, estima pelo tamanho do arquivo e o bitrate.
    """
    inicio = 0
    if dados[:3] == b'ID3':
        tamanho_tag = 0
        for byte in dados[6:10]:  # tamanho em formato "syncsafe" (7 bits por byte)
            tamanho_tag = (tamanho_tag << 7) | (byte & 0x7F)
        inicio = 10 + tamanho_tag

    # Procura a sincronização do frame: 11 bits ligados (0xFFE)
    posicao = inicio
    while posicao < len(dados) - 4:
        if dados[posicao] == 0xFF and (dados[posicao + 1] & 0xE0) == 0xE0:
            bitrate = BITRATES_KBPS[dados[posicao + 2] >> 4] * 1000
            taxa = TAXAS_AMOSTRAGEM[(dados[posicao + 2] >> 2) & 0x03]
            if bitrate and taxa:
                break
        posicao += 1
    else:
        return 0

    # Cabeçalho Xing/Info: fica depois do "side info" (32 bytes em estéreo, 17 em mono)
    mono = (dados[posicao + 3] >> 6) == 3
    pos_xing = posicao + 4 + (17 if mono else 32)
    if dados[pos_xing:pos_xing + 4] in (b'Xing', b'Info'):
        flags = struct.unpack('>I', dados[pos_xing + 4:pos_xing + 8])[0]
        if flags & 0x1:
            frames = struct.unpack('>I', dados[pos_xing + 8:pos_xing + 12])[0]
            return round(frames * 1152 / taxa)

    return round((len(dados) - posicao) * 8 / bitrate)


def baixar(url):
    """Baixa um arquivo e retorna os bytes."""
    pedido = urllib.request.Request(url, headers={'User-Agent': 'SomTeca/1.0 (projeto academico)'})
    with urllib.request.urlopen(pedido, timeout=120) as resposta:
        return resposta.read()


class Command(BaseCommand):
    help = 'Baixa 30 músicas reais (Kevin MacLeod, licença CC BY 4.0) e cadastra no banco.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reproducoes', type=int, default=800,
            help='Reproduções falsas a criar para essas faixas aparecerem nas mais tocadas (padrão: 800).',
        )

    def handle(self, *args, **opcoes):
        random.seed(7)
        pasta = Path(settings.MEDIA_ROOT) / PASTA_DESTINO
        pasta.mkdir(parents=True, exist_ok=True)

        artista, _ = Artista.objects.get_or_create(
            nome=ARTISTA['nome'],
            defaults={'pais_origem': ARTISTA['pais'], 'biografia': ARTISTA['bio']},
        )

        musicas = []
        total = sum(len(faixas) for _, _, faixas in COLETANEAS)
        contador = 0
        for indice, (titulo_album, genero, faixas) in enumerate(COLETANEAS):
            album, criado = Album.objects.get_or_create(
                titulo=titulo_album, artista=artista,
                defaults={'ano_lancamento': timezone.localdate().year, 'genero': genero},
            )
            if criado or not album.capa:
                cores = CORES_CAPA[indice % len(CORES_CAPA)]
                album.capa.save(f'capa-km-{slugify(titulo_album)}.png', ContentFile(gerar_capa(titulo_album, cores)))

            for numero, nome_arquivo in enumerate(faixas, start=1):
                contador += 1
                titulo = nome_arquivo.replace(' - ', ' (').replace('faster', 'Faster')
                if '(' in titulo:
                    titulo += ')'
                caminho_relativo = f'{PASTA_DESTINO}/{slugify(nome_arquivo)}.mp3'
                caminho = Path(settings.MEDIA_ROOT) / caminho_relativo

                # Baixa só se ainda não tiver o arquivo (dá para rodar o comando de novo)
                if not caminho.exists():
                    self.stdout.write(f'[{contador:2}/{total}] Baixando "{nome_arquivo}"...')
                    url = URL_BASE + urllib.parse.quote(nome_arquivo) + '.mp3'
                    try:
                        caminho.write_bytes(baixar(url))
                    except OSError as erro:
                        raise CommandError(f'Falha ao baixar {url}: {erro}') from erro
                else:
                    self.stdout.write(f'[{contador:2}/{total}] "{nome_arquivo}" já baixada.')

                musica, criada = Musica.objects.get_or_create(
                    album=album, numero_faixa=numero,
                    defaults={
                        'titulo': titulo,
                        'duracao': duracao_mp3(caminho.read_bytes()) or 180,
                        'arquivo_audio': caminho_relativo,
                    },
                )
                if criada:
                    musica.artistas.add(artista)
                musicas.append(musica)

        self.criar_playlist(musicas)
        if opcoes['reproducoes']:
            self.criar_reproducoes(musicas, opcoes['reproducoes'])

        self.stdout.write(self.style.SUCCESS(
            f'\nPronto! {len(musicas)} músicas reais de {artista.nome} em {len(COLETANEAS)} coletâneas.'
        ))
        self.stdout.write('Créditos: Kevin MacLeod (incompetech.com) — licença CC BY 4.0.')

    def criar_playlist(self, musicas):
        """Cria uma playlist pública com todas as faixas reais para o usuário demo (se existir)."""
        dono = User.objects.filter(username='demo').first() or User.objects.filter(is_superuser=True).first()
        if not dono:
            return
        playlist, _ = Playlist.objects.get_or_create(
            nome='Músicas Reais (CC BY)', usuario=dono,
            defaults={
                'descricao': 'Faixas de Kevin MacLeod (incompetech.com), licença Creative Commons BY 4.0.',
                'publica': True,
            },
        )
        for musica in musicas:
            playlist.adicionar_musica(musica)

    def criar_reproducoes(self, musicas, quantidade):
        """Plays falsos nos últimos meses, para as faixas aparecerem nas mais tocadas."""
        usuarios = list(User.objects.all()) + [None]
        agora = timezone.now()
        pesos = [random.random() ** 2 for _ in musicas]
        novas = [
            Reproducao(
                usuario=random.choice(usuarios),
                musica=random.choices(musicas, weights=pesos)[0],
                data_hora=agora - timedelta(days=int(random.triangular(0, 300, 0)), minutes=random.randint(0, 1439)),
            )
            for _ in range(quantidade)
        ]
        Reproducao.objects.bulk_create(novas, batch_size=500)
        for musica in musicas:
            Musica.objects.filter(pk=musica.pk).update(total_reproducoes=musica.reproducoes.count())
        self.stdout.write(f'{quantidade} reproduções criadas para as faixas reais.')
