from django.urls import path
from . import views as atendimento

urlpatterns = [
    path('', atendimento.AtendimentoCrud.as_view()),
    path('proposta-atendimento/', atendimento.PropostaAtendimento.as_view()),
    path('aceitar-atendimento/<int:atendimento_id>/', atendimento.AceitarAtendimento.as_view()),
    path('get-propostas/', atendimento.GetPropostas.as_view()),
    path("finalizar-atendimento/<int:atendimento_id>/", atendimento.TerminarAtendimento.as_view()),
    path("negar-atendimento/<int:atendimento_id>/", atendimento.NegarAtendimento.as_view()),
    path('reagendar-atendimento/', atendimento.ReagendarAtendimento.as_view()),
]