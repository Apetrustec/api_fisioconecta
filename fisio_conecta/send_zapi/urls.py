from django.urls import path
from . import views as sendzapi

urlpatterns = [
  path('', sendzapi.Conexao.as_view()),
  path('EnviarCodigoVerificacao/', sendzapi.EnviarCodigoVerificacao.as_view()),
  path('VerificaCodigoWhatsApp/', sendzapi.VerificaCodigoWhatsApp.as_view()),
  path('webhook', sendzapi.webhook),

]