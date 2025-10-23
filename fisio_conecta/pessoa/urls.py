from django.urls import path
from . import views as pessoa

urlpatterns = [
    path('', pessoa.GerenciaPessoa.as_view()),
    path('cadastro/', pessoa.CreatePessoa.as_view()),
]