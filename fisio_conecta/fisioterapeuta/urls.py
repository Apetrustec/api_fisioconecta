from django.urls import path
from . import views as fisioterapeuta

urlpatterns = [
    path('', fisioterapeuta.Crud.as_view()),
    path('por-atendimento/', fisioterapeuta.TodosPorAtendimento.as_view()),
]