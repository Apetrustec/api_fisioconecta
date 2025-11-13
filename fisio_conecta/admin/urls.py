from django.urls import path
from . import views as admin

urlpatterns = [
    path('pessoas-admin/', admin.PessoaAdminView.as_view()),
    path('atendimento-admin/', admin.AtendimentoAdminView.as_view()),
    path('Relatorio-ativos/', admin.RelatorioView.as_view()),
    path('status-fisioterapeuta/', admin.MudarStatusFisioterapeutaView.as_view()),
    path('status-paciente/', admin.MudarStatusPacienteView.as_view()),
    path('avaliacoes-admin/', admin.ListarAvaliacoesAdmin.as_view()),
    path('verificar-admin/', admin.LoginAdmin.as_view()),
    path('cadastrar-especialidade/', admin.EspecialidadeAdmin.as_view()),
    path('cadastrar-admin/', admin.cadastrarAdminOrGetAdmin.as_view()),
]