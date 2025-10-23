from django.urls import path
from . import views as checkin

urlpatterns = [
    path('checkin-por-paciente/<int:pk>/', checkin.CheckInOutPorPaciente.as_view()),
    path('', checkin.CheckinView.as_view()),
]
