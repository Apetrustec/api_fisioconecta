from django.urls import path
from . import views as paciente

urlpatterns = [
    path('', paciente.Crud.as_view()),
]