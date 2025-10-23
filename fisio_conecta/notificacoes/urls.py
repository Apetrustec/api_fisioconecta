from django.urls import path
from . import views as Notificacoes

urlpatterns = [
    path('cadastrar-dispositivo/', Notificacoes.CadastrarDispositivo.as_view()),
    path('notificacao-admin/', Notificacoes.NotificacaoAdmin.as_view()),
    path('teste-topico/', Notificacoes.TestPushNotificationTopic.as_view()),
    # path('teste-multicast/', Notificacoes.TestMulticastNotification.as_view())
]