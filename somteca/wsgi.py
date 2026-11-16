"""Configuração WSGI do projeto SomTeca (usada por servidores de produção)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somteca.settings')

application = get_wsgi_application()
