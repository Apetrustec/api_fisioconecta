from django.urls import path
from . import views as avaliacao

urlpatterns = [
    path('', avaliacao.AvaliacaoCrud.as_view()),
    path('poratendimento/', avaliacao.AvaliacaoPorAtendimento.as_view()),
    path('porFisio/', avaliacao.AvaliacaoFisioterapeuta.as_view()),
    path('porPaciente/', avaliacao.AvaliacaoPaciente.as_view())
]
