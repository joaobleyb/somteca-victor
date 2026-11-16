"""
Configurações do projeto SomTeca.

Este arquivo é pensado para ambiente de desenvolvimento (projeto acadêmico).
Para colocar em produção seria preciso trocar a SECRET_KEY, desligar o DEBUG
e configurar ALLOWED_HOSTS e os arquivos estáticos.
"""
from pathlib import Path

# Pasta raiz do projeto (onde fica o manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# ATENÇÃO: chave apenas para desenvolvimento. Nunca use esta chave em produção.
SECRET_KEY = 'django-insecure-somteca-projeto-academico-ifrs-troque-esta-chave'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ---------------------------------------------------------------------------
# Aplicações instaladas
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Apps nativos do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps do projeto
    'musica.apps.MusicaConfig',
    'playlists.apps.PlaylistsConfig',
    'usuarios.apps.UsuariosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'somteca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pasta global de templates, organizada em subpastas por app
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'somteca.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados (SQLite)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Validação de senhas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Idioma e fuso horário
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos (CSS, JS) e de mídia (uploads)
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Onde ficam as fotos, capas e arquivos .mp3 enviados pelos usuários
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'musica:dashboard'
LOGOUT_REDIRECT_URL = 'musica:dashboard'


# ---------------------------------------------------------------------------
# Mensagens: usa as classes de alerta do Bootstrap
# ---------------------------------------------------------------------------
from django.contrib.messages import constants as messages  # noqa: E402

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Quantidade de itens por página nas listagens
ITENS_POR_PAGINA = 12
