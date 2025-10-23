import django_filters
from fisio_conecta.models import Paciente

class PacienteFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='pessoa__nome', lookup_expr='icontains')
    sobrenome = django_filters.CharFilter(field_name='pessoa__sobrenome', lookup_expr='icontains')
    cpf = django_filters.CharFilter(field_name='pessoa__cpf', lookup_expr='icontains')
    ativo = django_filters.BooleanFilter()

    class Meta:
        model = Paciente
        fields = ['nome', 'sobrenome', 'cpf', 'ativo']
