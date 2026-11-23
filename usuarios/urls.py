"""Rotas do app usuarios."""
from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('login/', views.EntrarView.as_view(), name='login'),
    path('logout/', views.SairView.as_view(), name='logout'),
]
