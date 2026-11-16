"""
Comando de gerenciamento que enche o banco com dados de exemplo.

Uso:
    python manage.py popular_banco            # adiciona os dados de exemplo
    python manage.py popular_banco --limpar   # apaga o catálogo antes de popular

Cria usuários, artistas (fictícios), álbuns com capas geradas pelo Pillow,
músicas com um arquivo .mp3 silencioso, playlists e milhares de reproduções
espalhadas pelos últimos ~14 meses, para testar o ranking e a retrospectiva.
"""
import random
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from musica.models import Album, Artista, Musica, Reproducao
from playlists.models import Playlist

# ---------------------------------------------------------------------------
# Dados de exemplo (todos fictícios)
# ---------------------------------------------------------------------------
ARTISTAS = [
    {
        'nome': 'Aurora Boreal', 'pais': 'Brasil',
        'bio': 'Cantora e compositora gaúcha que mistura MPB com sintetizadores.',
        'albuns': [
            ('Céu de Inverno', 2019, 'mpb', ['Minuano', 'Geada no Peito', 'Chimarrão às Seis', 'Pampa Azul', 'Fim de Tarde no Guaíba']),
            ('Luz Polar', 2023, 'pop', ['Neon do Sul', 'Brilho Frio', 'Coração Magnético', 'Noite Longa']),
        ],
    },
    {
        'nome': 'Os Trovadores do Asfalto', 'pais': 'Brasil',
        'bio': 'Banda de rock formada em Porto Alegre por quatro amigos do ensino técnico.',
        'albuns': [
            ('Garagem', 2015, 'rock', ['Primeiro Acorde', 'Volume no Máximo', 'Pneu Careca', 'Estrada Federal', 'Último Ônibus']),
            ('Concreto e Distorção', 2021, 'rock', ['Viaduto', 'Sinal Vermelho', 'Fumaça', 'Contramão']),
        ],
    },
    {
        'nome': 'MC Vento Sul', 'pais': 'Brasil',
        'bio': 'Rapper que conta histórias da periferia em rimas rápidas e batidas pesadas.',
        'albuns': [
            ('Rima de Quebrada', 2020, 'rap', ['Papo Reto', 'Corre Diário', 'Vento Contra', 'Sonho de Laje', 'Madrugada']),
        ],
    },
    {
        'nome': 'Lua Cheia Trio', 'pais': 'Portugal',
        'bio': 'Trio de jazz de Lisboa conhecido pelas improvisações ao piano.',
        'albuns': [
            ('Sessões de Alfama', 2018, 'jazz', ['Elétrico 28', 'Miradouro', 'Fado em Si Bemol', 'Tejo ao Luar']),
            ('Maré Baixa', 2024, 'jazz', ['Gaivotas', 'Sal e Saudade', 'Farol']),
        ],
    },
    {
        'nome': 'Samba da Vila Nova', 'pais': 'Brasil',
        'bio': 'Roda de samba que virou grupo, com muito pandeiro, cavaquinho e alegria.',
        'albuns': [
            ('Roda de Domingo', 2017, 'samba', ['Pagode no Quintal', 'Feijoada', 'Batuque de Mesa', 'Saudade da Vila']),
        ],
    },
    {
        'nome': 'Pixel Drive', 'pais': 'Canadá',
        'bio': 'Dupla de música eletrônica inspirada em trilhas de videogames dos anos 90.',
        'albuns': [
            ('8 Bits of Love', 2022, 'eletronica', ['Insert Coin', 'Player Two', 'Boss Fight', 'Continue?', 'Game Over']),
        ],
    },
    {
        'nome': 'Rodeio Estrelado', 'pais': 'Brasil',
        'bio': 'Dupla sertaneja que canta amores, festas e saudades do interior.',
        'albuns': [
            ('Poeira da Estrada', 2021, 'sertanejo', ['Chapéu de Palha', 'Viola Chorona', 'Porteira Aberta', 'Lua de Fazenda']),
        ],
    },
    {
        'nome': 'Marina Indigo', 'pais': 'Argentina',
        'bio': 'Artista indie de Buenos Aires com letras intimistas e guitarras suaves.',
        'albuns': [
            ('Cuarto Azul', 2020, 'indie', ['Ventana', 'Domingo Lento', 'Café Frío', 'Las Luces']),
        ],
    },
]

# Participações especiais (feat.): (título da música, nome do artista convidado)
PARTICIPACOES = [
    ('Coração Magnético', 'Pixel Drive'),
    ('Vento Contra', 'Aurora Boreal'),
    ('Contramão', 'MC Vento Sul'),
    ('Sal e Saudade', 'Marina Indigo'),
    ('Saudade da Vila', 'Rodeio Estrelado'),
]

USUARIOS = [
    # (username, nome, senha)
    ('demo', 'Demo', 'somteca123'),
    ('ana', 'Ana', 'somteca123'),
    ('bruno', 'Bruno', 'somteca123'),
    ('carla', 'Carla', 'somteca123'),
]

CORES_CAPA = [
    ((29, 185, 84), (10, 60, 30)), ((255, 110, 199), (120, 20, 90)), ((255, 224, 102), (200, 110, 20)),
    ((79, 172, 254), (13, 60, 160)), ((179, 136, 255), (70, 40, 150)), ((255, 154, 90), (160, 50, 10)),
    ((80, 220, 200), (10, 90, 90)), ((240, 80, 80), (100, 10, 20)),
]


def gerar_mp3_silencioso(segundos=10):
    """
    Gera os bytes de um arquivo MP3 válido, só com silêncio.

    Um MP3 é uma sequência de "frames". Cada frame começa com um cabeçalho de
    4 bytes; se o resto do frame for zero, o decodificador toca silêncio.
    Cabeçalho usado: MPEG-1 Layer III, 32 kbps, 44.1 kHz, mono.
    """
    cabecalho = bytes([0xFF, 0xFB, 0x10, 0xC0])
    tamanho_frame = 144 * 32000 // 44100          # = 104 bytes por frame
    frames = int(segundos * 44100 / 1152)          # cada frame tem 1152 amostras
    frame = cabecalho + bytes(tamanho_frame - len(cabecalho))
    return frame * frames


def gerar_capa(texto, cores):
    """Cria uma capa quadrada em degradê com o texto (usa o Pillow). Retorna bytes PNG."""
    from PIL import Image, ImageDraw, ImageFont

    tamanho = 400
    inicio, fim = cores
    imagem = Image.new('RGB', (tamanho, tamanho))
    desenho = ImageDraw.Draw(imagem)
    # Degradê na diagonal: desenha linhas horizontais de cores intermediárias
    for y in range(tamanho):
        t = y / tamanho
        cor = tuple(int(inicio[i] + (fim[i] - inicio[i]) * t) for i in range(3))
        desenho.line([(0, y), (tamanho, y)], fill=cor)

    try:
        fonte = ImageFont.load_default(size=36)
    except TypeError:  # versões antigas do Pillow não aceitam size
        fonte = ImageFont.load_default()

    # Quebra o título em linhas curtas
    palavras, linhas, linha = texto.split(), [], ''
    for palavra in palavras:
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
    help = 'Popula o banco com artistas, álbuns, músicas, playlists e reproduções de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar', action='store_true',
            help='Apaga artistas, álbuns, músicas, playlists e reproduções antes de popular.',
        )
        parser.add_argument(
            '--reproducoes', type=int, default=4000,
            help='Quantidade de reproduções falsas a criar (padrão: 4000).',
        )

    @transaction.atomic
    def handle(self, *args, **opcoes):
        random.seed(42)  # resultados sempre iguais, bom para apresentações

        if opcoes['limpar']:
            self.stdout.write('Apagando dados antigos...')
            Reproducao.objects.all().delete()
            Playlist.objects.all().delete()
            Artista.objects.all().delete()  # em cascata apaga álbuns e músicas

        usuarios = self.criar_usuarios()
        musicas = self.criar_catalogo()
        self.criar_playlists(usuarios, musicas)
        self.criar_reproducoes(usuarios, musicas, opcoes['reproducoes'])

        self.stdout.write(self.style.SUCCESS(
            f'\nPronto! {Artista.objects.count()} artistas, {Album.objects.count()} álbuns, '
            f'{Musica.objects.count()} músicas, {Playlist.objects.count()} playlists e '
            f'{Reproducao.objects.count()} reproduções no banco.'
        ))
        self.stdout.write('Entre com o usuário "demo" e a senha "somteca123" para ver a retrospectiva.')

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

    def criar_catalogo(self):
        # Um único mp3 silencioso, compartilhado por todas as músicas de exemplo
        caminho_mp3 = 'musicas/exemplo-silencio.mp3'
        if not default_storage.exists(caminho_mp3):
            caminho_mp3 = default_storage.save(caminho_mp3, ContentFile(gerar_mp3_silencioso()))

        musicas = []
        agora = timezone.now()
        for i, dados in enumerate(ARTISTAS):
            artista, _ = Artista.objects.get_or_create(
                nome=dados['nome'], defaults={'pais_origem': dados['pais'], 'biografia': dados['bio']},
            )
            for j, (titulo, ano, genero, faixas) in enumerate(dados['albuns']):
                album, criado = Album.objects.get_or_create(
                    titulo=titulo, artista=artista,
                    defaults={'ano_lancamento': ano, 'genero': genero},
                )
                if criado:
                    cores = CORES_CAPA[(i + j) % len(CORES_CAPA)]
                    album.capa.save(f'capa-{album.pk}.png', ContentFile(gerar_capa(titulo, cores)))

                for numero, titulo_faixa in enumerate(faixas, start=1):
                    musica, criada = Musica.objects.get_or_create(
                        album=album, numero_faixa=numero,
                        defaults={
                            'titulo': titulo_faixa,
                            'duracao': random.randint(150, 330),
                            'arquivo_audio': caminho_mp3,
                        },
                    )
                    if criada:
                        musica.artistas.add(artista)
                        # Espalha as datas de cadastro para a lista de "recentes" ficar variada
                        Musica.objects.filter(pk=musica.pk).update(
                            data_criacao=agora - timedelta(days=random.randint(0, 120))
                        )
                    musicas.append(musica)

        # Participações especiais
        for titulo, convidado in PARTICIPACOES:
            musica = Musica.objects.filter(titulo=titulo).first()
            artista = Artista.objects.filter(nome=convidado).first()
            if musica and artista:
                musica.artistas.add(artista)

        self.stdout.write(f'Catálogo: {len(musicas)} músicas prontas.')
        return musicas

    def criar_playlists(self, usuarios, musicas):
        modelos = [
            ('Para Estudar', 'Foco total para as provas do IFRS.', True, ['jazz', 'indie', 'eletronica']),
            ('Treino Pesado', 'Energia para a academia.', True, ['rock', 'rap', 'eletronica']),
            ('Domingo em Casa', 'Samba, MPB e chimarrão.', True, ['samba', 'mpb', 'sertanejo']),
            ('Só Minhas', 'Uma playlist privada de exemplo.', False, ['pop', 'indie']),
        ]
        for usuario in usuarios:
            for nome, descricao, publica, generos in random.sample(modelos, 2):
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
        "músicas favoritas" com mais peso, para o ranking e a retrospectiva
        ficarem interessantes (e diferentes entre usuários).
        """
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
