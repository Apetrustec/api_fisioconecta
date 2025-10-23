from django.urls import include, path, re_path
from django.views.generic.base import TemplateView

from . import views as globalviews

urlpatterns = [
    path('fisioterapeuta/', include('fisio_conecta.fisioterapeuta.urls')),
    path('paciente/', include('fisio_conecta.paciente.urls')),
    # path('especialidade/', include('fisio_conecta.especialidade.urls')),
    path('atendimento/', include('fisio_conecta.atendimento.urls')),
    path('avaliacao/', include('fisio_conecta.avaliacao.urls')),
    path('admin/', include('fisio_conecta.admin.urls')),
    path('pessoa/', include('fisio_conecta.pessoa.urls')),
    path('sendzapi/', include('fisio_conecta.send_zapi.urls')),
    path('notificacoes/', include('fisio_conecta.notificacoes.urls')),
    path('checkin/', include('fisio_conecta.checkin.urls')),
]

urlpatterns += [# Apenas esse não funciona
    re_path(r'^fisio_admin/service-worker(.*.js)$', globalviews.fisio_admin_serviceworker, name='fisio_admin_serviceworker'),
    re_path(r'^fisio_admin/robots(.*.txt)$', globalviews.fisio_admin_robots, name='fisio_admin/robots'),
    re_path(r'^fisio_admin/.*$', TemplateView.as_view(template_name="fisio_admin/index.html")),
]